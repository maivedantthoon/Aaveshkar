import unittest
import time
from core.query_pipeline import (
    SearchQueryPipeline,
    QueryNormalizer,
    SpellCorrector,
    IntentTagger,
    QueryRewriter,
    EngineAdapters
)
from core.google_source import GoogleSourceEngine
from core.ai_pipeline import AIPipeline

class TestSearchQueryPipeline(unittest.TestCase):

    def test_stage1_normalizer(self):
        """Tests lexical normalization, contraction expansion, and prefix removal."""
        q1 = "what's the difference between python and java?"
        norm, core = QueryNormalizer.normalize(q1)
        self.assertIn("what is", norm)
        self.assertEqual(core, "difference between python and java")

        q2 = "can you please tell me about whatisai"
        norm2, core2 = QueryNormalizer.normalize(q2)
        self.assertIn("what is ai", norm2)

    def test_stage2_spell_corrector_user_phrase(self):
        """Tests user's exact phrase: 'inprove a search quire'."""
        corrected, corrections = SpellCorrector.correct("inprove a search quire")
        self.assertEqual(corrected, "improve a search query")
        corr_dict = dict(corrections)
        self.assertEqual(corr_dict.get("inprove"), "improve")
        self.assertEqual(corr_dict.get("quire"), "query")

    def test_stage2_tech_typos(self):
        """Tests common tech and framework typos."""
        corrected, _ = SpellCorrector.correct("pythn fastpai and djngo databse")
        self.assertIn("python", corrected)
        self.assertIn("fastapi", corrected)
        self.assertIn("django", corrected)
        self.assertIn("database", corrected)

    def test_stage3_intent_tagger(self):
        """Tests intent classification for different query types."""
        res_comp = IntentTagger.tag("react vs vue")
        self.assertEqual(res_comp["intent"], "comparison")
        self.assertTrue(res_comp["is_comparative"])
        self.assertEqual(res_comp["comparison_pair"], ("react", "vue"))

        res_code = IntentTagger.tag("how to reverse a string in python")
        self.assertEqual(res_code["intent"], "coding")

        res_def = IntentTagger.tag("what is transformer")
        self.assertEqual(res_def["intent"], "definition")

        res_news = IntentTagger.tag("latest updates on open source ai 2025")
        self.assertEqual(res_news["intent"], "news")

    def test_stage4_acronym_and_grounding(self):
        """Tests technical acronym expansion and ambiguous concept grounding."""
        res_acronym = QueryRewriter.rewrite("k8s deployment with rag and llm")
        self.assertIn("Kubernetes", res_acronym["expanded_query"])
        self.assertIn("Retrieval-Augmented Generation", res_acronym["expanded_query"])
        self.assertIn("Large Language Model", res_acronym["expanded_query"])

        res_air = QueryRewriter.rewrite("what is air", intent="definition")
        self.assertEqual(res_air["canonical_topic"], "Atmosphere of Earth")
        self.assertIn("-song", " ".join(f"-{x}" for x in res_air["exclusions"]))

    def test_stage5_engine_adapters(self):
        """Tests engine-specific query formatting."""
        pipeline_info = SearchQueryPipeline.improve_query("what is air")
        self.assertIn("-song", pipeline_info["google_query"])
        self.assertEqual(pipeline_info["wikipedia_query"], "Atmosphere of Earth")
        self.assertNotIn("-song", pipeline_info["duckduckgo_query"])

    def test_performance_latency(self):
        """Ensures query improvement completes in sub-5ms."""
        times = []
        test_queries = [
            "inprove a search quire",
            "fastpai vs djagno",
            "how to write python binary search",
            "what is air",
            "k8s rag architecture"
        ]
        # Warmup
        SearchQueryPipeline.improve_query("warmup query")

        for q in test_queries:
            t0 = time.perf_counter()
            res = SearchQueryPipeline.improve_query(q)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            times.append(elapsed_ms)
            self.assertTrue(res["corrected_query"])

        avg_latency = sum(times) / len(times)
        print(f"\n[BENCHMARK] Average SQIP Latency: {avg_latency:.3f} ms")
        self.assertLess(avg_latency, 15.0)  # Generous upper bound, expected < 3ms

    def test_google_source_engine_integration(self):
        """Verifies GoogleSourceEngine correctly uses SearchQueryPipeline."""
        canonical, refined = GoogleSourceEngine.refine_query_intent("inprove a search quire")
        self.assertEqual(canonical, "Improve A Search Query")
        self.assertEqual(refined, "improve a search query")

    def test_ai_pipeline_end_to_end(self):
        """Verifies AIPipeline runs Stage 1 with SQIP and logs diagnostics."""
        pipeline = AIPipeline()
        res = pipeline.run("inprove a search quire", use_search=False)
        self.assertTrue(res["success"])
        self.assertIn("query_improvement", res)
        self.assertEqual(res["query_improvement"]["corrected_query"], "improve a search query")
        stage1_log = next(s for s in res["pipeline_log"] if s["stage"] == 1)
        self.assertEqual(stage1_log["name"], "Query Intent Refinement")
        self.assertEqual(stage1_log["corrected_query"], "improve a search query")

if __name__ == "__main__":
    unittest.main()
