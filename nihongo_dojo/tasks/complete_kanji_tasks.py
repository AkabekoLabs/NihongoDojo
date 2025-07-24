"""
完全な常用漢字データベースを使用した漢字タスク生成
"""

import random
import uuid
from typing import List, Dict, Optional, Tuple
from ..core import JapaneseTask, TaskType, TaskDifficulty
from ..kanji.joyo_kanji_complete import (
    ALL_JOYO_KANJI,
    GRADE_KANJI_MAP,
    get_kanji_by_grade,
    get_kanji_by_grades,
    search_kanji
)
from ..kanji.compound_words import COMPOUND_WORDS_BY_GRADE, SINGLE_KANJI_WORDS


class CompleteKanjiTask:
    """完全な常用漢字データベースを使用した漢字タスク生成"""
    
    def __init__(self):
        # 難易度と学年のマッピング
        self.difficulty_grade_map = {
            TaskDifficulty.BEGINNER: [1, 2],        # 小学1-2年
            TaskDifficulty.INTERMEDIATE: [3, 4, 5], # 小学3-5年
            TaskDifficulty.ADVANCED: [6, 7, 8],     # 小学6年-中学2年
            TaskDifficulty.NATIVE: [9, 10]          # 中学3年-その他
        }
    
    def generate_reading_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """漢字読みタスクを生成"""
        # 難易度に応じた学年の漢字を取得
        grades = self.difficulty_grade_map[difficulty]
        kanji_list = get_kanji_by_grades(grades)
        
        if not kanji_list:
            # フォールバック
            kanji_list = get_kanji_by_grade(1)
        
        # ランダムに漢字を選択
        kanji_data = random.choice(kanji_list)
        kanji_char = kanji_data["kanji"]
        
        # 音読み・訓読みからランダムに選択
        readings = []
        reading_types = []
        
        if kanji_data.get("on_yomi"):
            on_yomi = kanji_data["on_yomi"]
            if isinstance(on_yomi, list):
                readings.extend(on_yomi)
                reading_types.extend(["on"] * len(on_yomi))
            else:
                readings.append(on_yomi)
                reading_types.append("on")
        
        if kanji_data.get("kun_yomi"):
            kun_yomi = kanji_data["kun_yomi"]
            if isinstance(kun_yomi, list):
                readings.extend(kun_yomi)
                reading_types.extend(["kun"] * len(kun_yomi))
            else:
                readings.append(kun_yomi)
                reading_types.append("kun")
        
        if not readings:
            # 読みが見つからない場合のフォールバック
            readings = ["読み方なし"]
            reading_types = ["none"]
        
        # ランダムに読みを選択
        idx = random.randint(0, len(readings) - 1)
        selected_reading = readings[idx]
        reading_type = reading_types[idx]
        
        # 読みタイプのラベル
        type_label = "音読み" if reading_type == "on" else "訓読み"
        
        # 例文の生成（可能であれば）
        examples = kanji_data.get("examples", [])
        example_text = ""
        if examples and isinstance(examples, list) and len(examples) > 0:
            example = random.choice(examples)
            if isinstance(example, dict):
                example_text = f"\n例: {example.get('word', '')} ({example.get('reading', '')})"
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KANJI_READING,
            difficulty=difficulty,
            instruction=f"次の漢字の{type_label}をひらがなで答えてください。",
            context=None,
            question=f"「{kanji_char}」の{type_label}は？{example_text}",
            answer=selected_reading,
            explanation=f"「{kanji_char}」の{type_label}は「{selected_reading}」です。",
            metadata={
                "kanji": kanji_char,
                "reading_type": reading_type,
                "grade": kanji_data.get("grade", "unknown"),
                "all_readings": {
                    "on_yomi": kanji_data.get("on_yomi", []),
                    "kun_yomi": kanji_data.get("kun_yomi", [])
                }
            }
        )
    
    def generate_writing_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """漢字書きタスクを生成"""
        # 難易度に応じた学年の漢字を取得
        grades = self.difficulty_grade_map[difficulty]
        kanji_list = get_kanji_by_grades(grades)
        
        if not kanji_list:
            # フォールバック
            kanji_list = get_kanji_by_grade(1)
        
        # ランダムに漢字を選択
        kanji_data = random.choice(kanji_list)
        kanji_char = kanji_data["kanji"]
        
        # 訓読みを優先的に使用（より自然な日本語のため）
        reading = None
        reading_type = None
        
        if kanji_data.get("kun_yomi"):
            kun_yomi = kanji_data["kun_yomi"]
            if isinstance(kun_yomi, list) and len(kun_yomi) > 0:
                reading = random.choice(kun_yomi)
                reading_type = "kun"
            elif isinstance(kun_yomi, str):
                reading = kun_yomi
                reading_type = "kun"
        
        # 訓読みがない場合は音読みを使用
        if not reading and kanji_data.get("on_yomi"):
            on_yomi = kanji_data["on_yomi"]
            if isinstance(on_yomi, list) and len(on_yomi) > 0:
                reading = random.choice(on_yomi)
                reading_type = "on"
            elif isinstance(on_yomi, str):
                reading = on_yomi
                reading_type = "on"
        
        if not reading:
            # 読みが見つからない場合は次の漢字を試す
            return self.generate_writing_task(difficulty)
        
        # ひらがなに変換（カタカナの音読みをひらがなに）
        if reading_type == "on":
            reading_hiragana = self._katakana_to_hiragana(reading)
        else:
            reading_hiragana = reading
        
        # 例文の生成
        examples = kanji_data.get("examples", [])
        context_text = None
        if examples and isinstance(examples, list) and len(examples) > 0:
            example = random.choice(examples)
            if isinstance(example, dict):
                word = example.get('word', '')
                word_reading = example.get('reading', '')
                context_text = f"例: 「{word_reading}」は「{word}」と書きます。"
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KANJI_WRITING,
            difficulty=difficulty,
            instruction="次のひらがなを漢字で書いてください。",
            context=context_text,
            question=f"「{reading_hiragana}」を漢字で書くと？",
            answer=kanji_char,
            explanation=f"「{reading_hiragana}」は「{kanji_char}」と書きます。",
            metadata={
                "kanji": kanji_char,
                "reading": reading_hiragana,
                "reading_type": reading_type,
                "grade": kanji_data.get("grade", "unknown"),
                "all_readings": {
                    "on_yomi": kanji_data.get("on_yomi", []),
                    "kun_yomi": kanji_data.get("kun_yomi", [])
                }
            }
        )
    
    def generate_practical_writing_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """実用的な単漢字書き取りタスクを生成"""
        # 難易度に応じた単語リストを取得
        difficulty_map = {
            TaskDifficulty.BEGINNER: "beginner",
            TaskDifficulty.INTERMEDIATE: "intermediate",
            TaskDifficulty.ADVANCED: "advanced",
            TaskDifficulty.NATIVE: "native"
        }
        
        word_list = SINGLE_KANJI_WORDS.get(difficulty_map[difficulty], SINGLE_KANJI_WORDS["beginner"])
        reading, kanji, context = random.choice(word_list)
        
        # 文脈を使った問題文を作成
        question_with_context = context.replace("［　］", f"「{reading}」")
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KANJI_WRITING,
            difficulty=difficulty,
            instruction="次のひらがなを漢字で書いてください。",
            context=context,
            question=f"{question_with_context}の「{reading}」を漢字で書くと？",
            answer=kanji,
            explanation=f"「{reading}」は「{kanji}」と書きます。",
            metadata={
                "word": kanji,
                "reading": reading,
                "context": context,
                "type": "practical_single"
            }
        )
    
    def generate_practical_compound_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """実用的な熟語書き取りタスクを生成"""
        # 難易度に応じた熟語リストを取得
        difficulty_map = {
            TaskDifficulty.BEGINNER: "beginner",
            TaskDifficulty.INTERMEDIATE: "intermediate",
            TaskDifficulty.ADVANCED: "advanced",
            TaskDifficulty.NATIVE: "native"
        }
        
        compound_list = COMPOUND_WORDS_BY_GRADE.get(difficulty_map[difficulty], COMPOUND_WORDS_BY_GRADE["beginner"])
        compound, reading, meaning, grades = random.choice(compound_list)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KANJI_WRITING,
            difficulty=difficulty,
            instruction="次の読みを漢字で書いてください。",
            context=f"意味: {meaning}",
            question=f"「{reading}」を漢字で書くと？",
            answer=compound,
            explanation=f"「{reading}」は「{compound}」と書きます。（{meaning}）",
            metadata={
                "compound": compound,
                "reading": reading,
                "meaning": meaning,
                "grades": grades,
                "type": "practical_compound"
            }
        )
    
    def generate_compound_writing_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """熟語の書き取りタスクを生成"""
        # 難易度に応じた学年の漢字を取得
        grades = self.difficulty_grade_map[difficulty]
        kanji_list = get_kanji_by_grades(grades)
        
        # 2つの漢字を選択して熟語を作る
        if len(kanji_list) < 2:
            return self.generate_writing_task(difficulty)
        
        # ランダムに2つの漢字を選択
        kanji1_data, kanji2_data = random.sample(kanji_list, 2)
        kanji1 = kanji1_data["kanji"]
        kanji2 = kanji2_data["kanji"]
        
        # 音読みを取得（熟語は通常音読み）
        reading1 = self._get_first_on_yomi(kanji1_data)
        reading2 = self._get_first_on_yomi(kanji2_data)
        
        if not reading1 or not reading2:
            # 音読みがない場合は単漢字タスクにフォールバック
            return self.generate_writing_task(difficulty)
        
        compound = kanji1 + kanji2
        compound_reading = self._katakana_to_hiragana(reading1 + reading2)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KANJI_WRITING,
            difficulty=difficulty,
            instruction="次の読みを漢字で書いてください。",
            context="※2文字の熟語です",
            question=f"「{compound_reading}」を漢字で書くと？",
            answer=compound,
            explanation=f"「{compound_reading}」は「{compound}」と書きます。「{kanji1}」({reading1}) + 「{kanji2}」({reading2})",
            metadata={
                "compound": compound,
                "reading": compound_reading,
                "kanji1": kanji1,
                "kanji2": kanji2,
                "grade1": kanji1_data.get("grade", "unknown"),
                "grade2": kanji2_data.get("grade", "unknown")
            }
        )
    
    def _katakana_to_hiragana(self, text: str) -> str:
        """カタカナをひらがなに変換"""
        result = []
        for char in text:
            code = ord(char)
            if 0x30A1 <= code <= 0x30F6:  # カタカナの範囲
                result.append(chr(code - 0x60))
            else:
                result.append(char)
        return ''.join(result)
    
    def _get_first_on_yomi(self, kanji_data: dict) -> Optional[str]:
        """最初の音読みを取得"""
        on_yomi = kanji_data.get("on_yomi")
        if isinstance(on_yomi, list) and len(on_yomi) > 0:
            return on_yomi[0]
        elif isinstance(on_yomi, str):
            return on_yomi
        return None