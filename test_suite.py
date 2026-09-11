import sys
import os
import unittest
import asyncio

# Ensure UTF-8 output across Windows consoles
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from executors.script_executor import ScriptExecutor
from executors.system_executor import SystemExecutor
from core.intent_parser import IntentParser
from core.task_planner import TaskPlanner
from core.custom_transformer import TransformerEngine
from core.google_source import GoogleSourceEngine

class TestAssistantCore(unittest.TestCase):
    def test_script_executor_python(self):
        res = ScriptExecutor.execute("python", "print(10 + 25)")
        self.assertTrue(res.get("success"))
        self.assertIn("35", res.get("stdout", ""))

    def test_system_stats(self):
        stats = SystemExecutor.get_system_stats()
        self.assertIn("cpu_usage_percent", stats)
        self.assertIn("ram_used_percent", stats)

    def test_intent_parsing_browser(self):
        parser = IntentParser()
        parsed = parser.parse("open https://github.com")
        self.assertEqual(parsed.get("category"), "browser")
        self.assertEqual(parsed.get("action"), "navigate")

    def test_intent_parsing_app(self):
        parser = IntentParser()
        parsed = parser.parse("launch notepad")
        self.assertEqual(parsed.get("category"), "system")
        self.assertEqual(parsed.get("action"), "launch_app")

    def test_task_planner_code_exec(self):
        planner = TaskPlanner(browser_headless=True, voice_enabled=False)
        result = asyncio.run(planner.execute_task("run python: print('Testing execution framework')"))
        self.assertEqual(result.get("status"), "success")
        self.assertIn("Testing execution framework", result.get("output", {}).get("stdout", ""))

    def test_intent_parsing_greeting(self):
        parser = IntentParser()
        parsed = parser.parse("hello")
        self.assertEqual(parsed.get("category"), "chat")
        self.assertIn("Hello", parsed.get("params", {}).get("response", ""))

    def test_intent_parsing_math(self):
        parser = IntentParser()
        parsed = parser.parse("calculate 25 * 40")
        self.assertEqual(parsed.get("category"), "chat")
        self.assertIn("1,000", parsed.get("params", {}).get("response", ""))

        pct_parsed = parser.parse("15% of 200")
        self.assertIn("30", pct_parsed.get("params", {}).get("response", ""))

    def test_intent_parsing_volume(self):
        parser = IntentParser()
        parsed = parser.parse("volume up")
        self.assertEqual(parsed.get("category"), "system")
        self.assertEqual(parsed.get("action"), "change_volume")
        self.assertEqual(parsed.get("params", {}).get("action"), "up")

    def test_intent_parsing_weather(self):
        parser = IntentParser()
        parsed = parser.parse("weather Tokyo")
        self.assertEqual(parsed.get("category"), "browser")
        self.assertEqual(parsed.get("action"), "search_weather")
        self.assertEqual(parsed.get("params", {}).get("city"), "tokyo")

    def test_intent_parsing_coding_prompt(self):
        parser = IntentParser()
        parsed = parser.parse("write python code to calculate factorial")
        self.assertEqual(parsed.get("category"), "transformer")
        self.assertEqual(parsed.get("action"), "generate")

    def test_custom_transformer_answers(self):
        engine = TransformerEngine.get_instance()
        ans = engine.generate_answer("what is transformer")
        self.assertIn("Transformer", ans.get("main_answer", ""))
        self.assertTrue(len(ans.get("bullet_points", [])) >= 3)
        self.assertIn("self-attention", ans.get("formatted_markdown", "").lower())

    def test_custom_transformer_python(self):
        engine = TransformerEngine.get_instance()
        ans = engine.generate_answer("what is python")
        self.assertIn("Python", ans.get("main_answer", ""))
        self.assertIn("Guido van Rossum", ans.get("main_answer", ""))

    def test_google_disambiguation_map(self):
        self.assertEqual(
            GoogleSourceEngine.DISAMBIGUATION_MAP.get("transformer"),
            "Transformer (deep learning architecture)"
        )
        self.assertEqual(
            GoogleSourceEngine.DISAMBIGUATION_MAP.get("python"),
            "Python (programming language)"
        )

    def test_query_intent_refinement(self):
        canonical, refined = GoogleSourceEngine.refine_query_intent("what is air")
        self.assertEqual(canonical, "Atmosphere of Earth")
        self.assertIn("Earth atmospheric air", refined)

        canonical_apple, refined_apple = GoogleSourceEngine.refine_query_intent("what is apple")
        self.assertEqual(canonical_apple, "Apple")
        self.assertIn("Malus domestica", refined_apple)

    def test_noise_filtering_patterns(self):
        import re
        test_strings = [
            "Air is a 2015 American post-apocalyptic film directed by Christian Cantamessa.",
            "Air is the debut studio album by French electronic music duo Air.",
            "The AIM-7 Sparrow is an American, medium-range semi-active radar-homing air-to-air missile.",
            "MacBook Air is a line of laptop computers developed and manufactured by Apple Inc."
        ]
        for s in test_strings:
            matches = any(re.search(pat, s.lower()) for pat in GoogleSourceEngine.DISAMBIGUATION_NOISE_PATTERNS)
            self.assertTrue(matches, f"Expected noise pattern to match: {s}")

    def test_what_is_air_synthesis(self):
        engine = TransformerEngine.get_instance()
        ans = engine.generate_answer("what is air")
        md = ans.get("formatted_markdown", "").lower()
        self.assertIn("atmosphere", md)
        self.assertTrue("nitrogen" in md or "gases" in md)
        # Verify complete absence of noise
        self.assertNotIn("missile", md)
        self.assertNotIn("macbook", md)
        self.assertNotIn("soundtrack", md)

    def test_what_is_apple_synthesis(self):
        engine = TransformerEngine.get_instance()
        ans = engine.generate_answer("what is apple")
        md = ans.get("formatted_markdown", "").lower()
        self.assertTrue("fruit" in md or "malus" in md)

    def test_ai_pipeline_end_to_end(self):
        from core.ai_pipeline import AIPipeline
        pipeline = AIPipeline()
        result = pipeline.run("what is air")
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("canonical_topic"), "Atmosphere of Earth")
        self.assertTrue(len(result.get("bullet_points", [])) >= 3)
        self.assertTrue(len(result.get("pipeline_log", [])) == 5)
        # Verify stage logging
        stages = [log["name"] for log in result.get("pipeline_log", [])]
        self.assertIn("Query Intent Refinement", stages)
        self.assertIn("Multi-Source Retrieval", stages)
        self.assertIn("Data Preprocessing & Noise Filtering", stages)
        self.assertIn("Neural Transformer Cross-Attention Re-ranking", stages)
        self.assertIn("Cognitive Synthesis & Citation Formatting", stages)

if __name__ == "__main__":
    unittest.main()
