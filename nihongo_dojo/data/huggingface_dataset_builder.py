"""
Hugging Face Dataset Builder for Nihongo DoJo
"""

import json
import random
from typing import List, Dict, Any, Optional
from datasets import Dataset, DatasetDict, Features, Value, ClassLabel
from ..tasks.complete_kanji_tasks import CompleteKanjiTask
from ..kanji import get_kanji_by_grade, get_kanji_by_grades
from ..core import TaskType, TaskDifficulty


class HuggingFaceDatasetBuilder:
    """Hugging Face用のデータセット構築クラス"""
    
    def __init__(self):
        self.kanji_task_generator = CompleteKanjiTask()
        # Kanji database is accessed through kanji module functions
        
        # Import other task generators
        from ..core import NihongoDoJo
        self.nihongo_dojo = NihongoDoJo()
    
    def _katakana_to_hiragana(self, text: str) -> str:
        """カタカナをひらがなに変換（長音符号、小文字、句読点も適切に処理）"""
        # カタカナ→ひらがな変換テーブル
        katakana_chart = {
            # 通常のカタカナ
            'ア': 'あ', 'イ': 'い', 'ウ': 'う', 'エ': 'え', 'オ': 'お',
            'カ': 'か', 'キ': 'き', 'ク': 'く', 'ケ': 'け', 'コ': 'こ',
            'ガ': 'が', 'ギ': 'ぎ', 'グ': 'ぐ', 'ゲ': 'げ', 'ゴ': 'ご',
            'サ': 'さ', 'シ': 'し', 'ス': 'す', 'セ': 'せ', 'ソ': 'そ',
            'ザ': 'ざ', 'ジ': 'じ', 'ズ': 'ず', 'ゼ': 'ぜ', 'ゾ': 'ぞ',
            'タ': 'た', 'チ': 'ち', 'ツ': 'つ', 'テ': 'て', 'ト': 'と',
            'ダ': 'だ', 'ヂ': 'ぢ', 'ヅ': 'づ', 'デ': 'で', 'ド': 'ど',
            'ナ': 'な', 'ニ': 'に', 'ヌ': 'ぬ', 'ネ': 'ね', 'ノ': 'の',
            'ハ': 'は', 'ヒ': 'ひ', 'フ': 'ふ', 'ヘ': 'へ', 'ホ': 'ほ',
            'バ': 'ば', 'ビ': 'び', 'ブ': 'ぶ', 'ベ': 'べ', 'ボ': 'ぼ',
            'パ': 'ぱ', 'ピ': 'ぴ', 'プ': 'ぷ', 'ペ': 'ぺ', 'ポ': 'ぽ',
            'マ': 'ま', 'ミ': 'み', 'ム': 'む', 'メ': 'め', 'モ': 'も',
            'ヤ': 'や', 'ユ': 'ゆ', 'ヨ': 'よ',
            'ラ': 'ら', 'リ': 'り', 'ル': 'る', 'レ': 'れ', 'ロ': 'ろ',
            'ワ': 'わ', 'ヰ': 'ゐ', 'ヱ': 'ゑ', 'ヲ': 'を', 'ン': 'ん',
            'ヴ': 'ゔ',
            # 小文字
            'ァ': 'ぁ', 'ィ': 'ぃ', 'ゥ': 'ぅ', 'ェ': 'ぇ', 'ォ': 'ぉ',
            'ヵ': 'ゕ', 'ヶ': 'ゖ',
            'ッ': 'っ', 'ャ': 'ゃ', 'ュ': 'ゅ', 'ョ': 'ょ',
            'ヮ': 'ゎ',
            # 長音符号はそのまま残す
            'ー': 'ー',
            # 句読点
            '・': '・', '、': '、', '。': '。',
        }
        
        # str.translate用のテーブルを作成
        translation_table = str.maketrans(katakana_chart)
        
        return text.translate(translation_table)
    
    def create_kanji_reading_dataset(
        self,
        num_samples_per_grade: int = 100,
        grades: List[int] = [1, 2, 3, 4, 5, 6],
        include_on_yomi: bool = True,
        include_kun_yomi: bool = True,
        include_writing: bool = False,
        split_ratio: Dict[str, float] = {"train": 0.8, "validation": 0.1, "test": 0.1}
    ) -> DatasetDict:
        """漢字読み書きデータセットを作成"""
        
        all_samples = []
        
        for grade in grades:
            grade_kanji = get_kanji_by_grade(grade, as_dict=True)
            
            for kanji_data in grade_kanji:
                # 音読みサンプル
                if include_on_yomi and kanji_data.get("on_yomi"):
                    for on_reading in kanji_data["on_yomi"]:
                        # 思考過程を生成
                        thinking = self._generate_thinking_process(
                            kanji_data['kanji'], 
                            'on_yomi',
                            on_reading,
                            kanji_data.get('meanings', []),
                            grade
                        )
                        
                        # 音読みをひらがなに変換
                        on_reading_hiragana = self._katakana_to_hiragana(on_reading)
                        
                        sample = {
                            "instruction": "次の漢字の音読み（おんよみ）をひらがなで答えてください。",
                            "input": f"「{kanji_data['kanji']}」の音読みは？",
                            "think": thinking,  # 思考過程（タグなし）
                            "answer": on_reading_hiragana,  # 解答（タグなし、ひらがなに変換）
                            "task_type": "kanji_reading_on",
                            "difficulty": self._grade_to_difficulty(grade),
                            "grade": grade,
                            "kanji": kanji_data["kanji"],
                            "all_on_yomi": kanji_data.get("on_yomi", []),
                            "all_kun_yomi": kanji_data.get("kun_yomi", []),
                            "meanings": kanji_data.get("meanings", []),
                            "stroke_count": kanji_data.get("stroke_count", 0),
                            # Add word-related fields for consistency
                            "word": None,
                            "reading_type": None
                        }
                        all_samples.append(sample)
                
                # 訓読みサンプル
                if include_kun_yomi and kanji_data.get("kun_yomi"):
                    for kun_reading in kanji_data["kun_yomi"]:
                        # 思考過程を生成
                        thinking = self._generate_thinking_process(
                            kanji_data['kanji'], 
                            'kun_yomi',
                            kun_reading,
                            kanji_data.get('meanings', []),
                            grade
                        )
                        
                        sample = {
                            "instruction": "次の漢字の訓読み（くんよみ）をひらがなで答えてください。",
                            "input": f"「{kanji_data['kanji']}」の訓読みは？",
                            "think": thinking,  # 思考過程（タグなし）
                            "answer": kun_reading,  # 解答（タグなし）
                            "task_type": "kanji_reading_kun",
                            "difficulty": self._grade_to_difficulty(grade),
                            "grade": grade,
                            "kanji": kanji_data["kanji"],
                            "all_on_yomi": kanji_data.get("on_yomi", []),
                            "all_kun_yomi": kanji_data.get("kun_yomi", []),
                            "meanings": kanji_data.get("meanings", []),
                            "stroke_count": kanji_data.get("stroke_count", 0),
                            # Add word-related fields for consistency
                            "word": None,
                            "reading_type": None
                        }
                        all_samples.append(sample)
                
                # 漢字書きサンプル
                if include_writing and kanji_data.get("kun_yomi"):
                    for kun_reading in kanji_data["kun_yomi"]:
                        # 思考過程を生成
                        thinking = self._generate_thinking_process(
                            kanji_data['kanji'], 
                            'writing',
                            kun_reading,
                            kanji_data.get('meanings', []),
                            grade
                        )
                        
                        sample = {
                            "instruction": "次のひらがなを漢字で書いてください。",
                            "input": f"「{kun_reading}」を漢字で書くと？",
                            "think": thinking,  # 思考過程（タグなし）
                            "answer": kanji_data['kanji'],  # 解答（タグなし）
                            "task_type": "kanji_writing",
                            "difficulty": self._grade_to_difficulty(grade),
                            "grade": grade,
                            "kanji": kanji_data["kanji"],
                            "all_on_yomi": kanji_data.get("on_yomi", []),
                            "all_kun_yomi": kanji_data.get("kun_yomi", []),
                            "meanings": kanji_data.get("meanings", []),
                            "stroke_count": kanji_data.get("stroke_count", 0),
                            # Add word-related fields for consistency
                            "word": None,
                            "reading_type": None
                        }
                        all_samples.append(sample)
                
                # 例文ベースのサンプル（現在のデータ形式にはexample_wordsがないためスキップ）
                # if kanji_data.get("example_words"):
                #     for word, reading, reading_type in kanji_data["example_words"]:
                #         sample = {
                #             "instruction": f"次の単語の読み方をひらがなで答えてください。",
                #             "input": f"「{word}」の読み方は？",
                #             "output": reading,
                #             "task_type": f"word_reading_{reading_type}",
                #             "difficulty": self._grade_to_difficulty(grade),
                #             "grade": grade,
                #             "kanji": kanji_data["kanji"],
                #             "word": word,
                #             "reading_type": reading_type,
                #             # Add the same fields as kanji reading samples to maintain consistency
                #             "all_on_yomi": kanji_data.get("on_yomi", []),
                #             "all_kun_yomi": kanji_data.get("kun_yomi", []),
                #             "meanings": kanji_data.get("meanings", []),
                #             "stroke_count": kanji_data.get("stroke_count", 0)
                #         }
                #         all_samples.append(sample)
        
        # シャッフル
        random.shuffle(all_samples)
        
        # 分割
        total_samples = len(all_samples)
        train_size = int(total_samples * split_ratio["train"])
        val_size = int(total_samples * split_ratio["validation"])
        
        train_samples = all_samples[:train_size]
        val_samples = all_samples[train_size:train_size + val_size]
        test_samples = all_samples[train_size + val_size:]
        
        # データセット作成
        train_dataset = Dataset.from_list(train_samples)
        val_dataset = Dataset.from_list(val_samples)
        test_dataset = Dataset.from_list(test_samples)
        
        return DatasetDict({
            "train": train_dataset,
            "validation": val_dataset,
            "test": test_dataset
        })
    
    def create_grpo_dataset(
        self,
        num_groups: int = 1000,
        group_size: int = 4,
        task_types: Optional[List[str]] = None
    ) -> Dataset:
        """GRPO学習用のグループ化されたデータセットを作成"""
        
        if task_types is None:
            task_types = ["kanji_reading_on", "kanji_reading_kun", "word_reading"]
        
        # TaskTypeオブジェクトの場合、適切に処理
        if task_types and hasattr(task_types[0], 'value'):
            # TaskTypeオブジェクトのリストをそのまま使用
            task_type_objects = task_types
        else:
            # 文字列の場合、TaskTypeオブジェクトに変換
            task_type_objects = [TaskType(t) if isinstance(t, str) else t for t in task_types]
        
        groups = []
        
        # 非漢字タスクの場合は別の処理
        non_kanji_tasks = [TaskType.PARTICLE_FILL, TaskType.KEIGO_CONVERSION, 
                          TaskType.WORD_ORDER, TaskType.COUNTER_WORD,
                          TaskType.ADVANCED_GRAMMAR, TaskType.ONOMATOPOEIA,
                          TaskType.CONVERSATION, TaskType.PROVERB_IDIOM,
                          TaskType.BUSINESS_JAPANESE, TaskType.CLASSICAL_JAPANESE,
                          TaskType.SPECIALIZED_VOCABULARY, TaskType.SEASONAL_EXPRESSION,
                          TaskType.SOCIAL_CONTEXT,
                          TaskType.REGIONAL_DIALECT, TaskType.AGE_GENDER_LANGUAGE,
                          TaskType.EMOTIONAL_EXPRESSION]
        
        # タスクタイプが非漢字タスクのみの場合
        if all(t in non_kanji_tasks for t in task_type_objects):
            for group_id in range(num_groups):
                group_samples = []
                
                # グループ内で同じ難易度を使用
                difficulty = random.choice([TaskDifficulty.BEGINNER, TaskDifficulty.INTERMEDIATE, 
                                          TaskDifficulty.ADVANCED])
                
                for i in range(group_size):
                    # ランダムにタスクタイプを選択
                    task_type = random.choice(task_type_objects)
                    
                    # NihongoDoJoでタスクを生成
                    task = self.nihongo_dojo.generate_task(task_type=task_type, difficulty=difficulty)
                    
                    # 思考過程を生成
                    thinking = f"{task.explanation or 'この問題について考えます。'} 答えは「{task.answer}」です。"
                    
                    sample = {
                        "group_id": group_id,
                        "sample_id": i,
                        "instruction": task.instruction,
                        "input": task.question,
                        "think": thinking,
                        "answer": task.answer if isinstance(task.answer, str) else str(task.answer),
                        "task_type": task_type.value
                    }
                    
                    group_samples.append(sample)
                
                groups.extend(group_samples)
            
            return Dataset.from_list(groups)
        
        # 漢字タスクを含む場合の既存の処理
        for group_id in range(num_groups):
            group_samples = []
            
            # グループ内で同じ漢字または関連する漢字を使用
            base_grade = random.choice([1, 2, 3, 4, 5, 6])
            kanji_list = get_kanji_by_grade(base_grade, as_dict=True)
            
            if len(kanji_list) >= group_size:
                selected_kanji = random.sample(kanji_list, group_size)
            else:
                selected_kanji = random.choices(kanji_list, k=group_size)
            
            for i, kanji_data in enumerate(selected_kanji):
                task_type = random.choice(task_types)
                
                sample = None
                
                if task_type == "kanji_writing":
                    # 漢字書きタスク
                    if kanji_data.get("kun_yomi"):
                        reading = random.choice(kanji_data["kun_yomi"])
                        thinking = self._generate_thinking_process(
                            kanji_data['kanji'], 
                            'writing',
                            reading,
                            kanji_data.get('meanings', []),
                            base_grade
                        )
                        sample = {
                            "group_id": group_id,
                            "sample_id": i,
                            "instruction": "次のひらがなを漢字で書いてください。",
                            "input": f"「{reading}」を漢字で書くと？",
                            "think": thinking,
                            "answer": kanji_data['kanji'],
                            "task_type": task_type
                        }
                    else:
                        # 訓読みがない場合は読みタスクにフォールバック
                        task_type = "kanji_reading_on"
                
                if task_type == "kanji_reading_on" and kanji_data.get("on_yomi"):
                    reading = random.choice(kanji_data["on_yomi"])
                    # 音読みをひらがなに変換
                    reading_hiragana = self._katakana_to_hiragana(reading)
                    thinking = self._generate_thinking_process(
                        kanji_data['kanji'], 
                        'on_yomi',
                        reading,
                        kanji_data.get('meanings', []),
                        base_grade
                    )
                    sample = {
                        "group_id": group_id,
                        "sample_id": i,
                        "instruction": "次の漢字の音読み（おんよみ）をひらがなで答えてください。",
                        "input": f"「{kanji_data['kanji']}」の音読みは？",
                        "think": thinking,
                        "answer": reading_hiragana,
                        "task_type": task_type
                    }
                elif task_type == "kanji_reading_kun" and kanji_data.get("kun_yomi"):
                    reading = random.choice(kanji_data["kun_yomi"])
                    thinking = self._generate_thinking_process(
                        kanji_data['kanji'], 
                        'kun_yomi',
                        reading,
                        kanji_data.get('meanings', []),
                        base_grade
                    )
                    sample = {
                        "group_id": group_id,
                        "sample_id": i,
                        "instruction": "次の漢字の訓読み（くんよみ）をひらがなで答えてください。",
                        "input": f"「{kanji_data['kanji']}」の訓読みは？",
                        "think": thinking,
                        "answer": reading,
                        "task_type": task_type
                    }
                else:
                    # フォールバック
                    output = kanji_data.get("on_yomi", [""])[0] if kanji_data.get("on_yomi") else kanji_data.get("kun_yomi", [""])[0] if kanji_data.get("kun_yomi") else ""
                    reading_type = 'on_yomi' if kanji_data.get("on_yomi") else 'kun_yomi'
                    # 音読みの場合はひらがなに変換
                    if reading_type == 'on_yomi' and output:
                        output = self._katakana_to_hiragana(output)
                    thinking = self._generate_thinking_process(
                        kanji_data['kanji'], 
                        reading_type,
                        output,
                        kanji_data.get('meanings', []),
                        base_grade
                    )
                    sample = {
                        "group_id": group_id,
                        "sample_id": i,
                        "instruction": "次の漢字の読み方をひらがなで答えてください。",
                        "input": f"「{kanji_data['kanji']}」の読み方は？",
                        "think": thinking,
                        "answer": output,
                        "task_type": "kanji_reading_general"
                    }
                
                if sample is not None:
                    group_samples.append(sample)
            
            groups.extend(group_samples)
        
        return Dataset.from_list(groups)
    
    def create_chat_format_dataset(
        self,
        num_samples: int = 1000,
        system_prompt: Optional[str] = None
    ) -> Dataset:
        """ChatGPT/Claude形式のデータセットを作成"""
        
        if system_prompt is None:
            system_prompt = "あなたは日本語教育の専門家です。学習者の質問に正確に答えてください。"
        
        samples = []
        
        for _ in range(num_samples):
            grade = random.choice([1, 2, 3, 4, 5, 6])
            grade_kanji = get_kanji_by_grade(grade, as_dict=True)
            
            if not grade_kanji:
                continue
                
            kanji_data = random.choice(grade_kanji)
            
            # 様々な質問パターン
            # 音読みをひらがなに変換
            on_yomi_hiragana = [self._katakana_to_hiragana(reading) for reading in kanji_data.get('on_yomi', [])]
            
            question_patterns = [
                (f"「{kanji_data['kanji']}」の音読みを教えてください。", 
                 f"「{kanji_data['kanji']}」の音読みは{', '.join(on_yomi_hiragana)}です。" if on_yomi_hiragana else f"「{kanji_data['kanji']}」には音読みがありません。"),
                
                (f"「{kanji_data['kanji']}」の訓読みを教えてください。",
                 f"「{kanji_data['kanji']}」の訓読みは{', '.join(kanji_data.get('kun_yomi', []))}です。" if kanji_data.get('kun_yomi') else f"「{kanji_data['kanji']}」には訓読みがありません。"),
                
                (f"「{kanji_data['kanji']}」の意味を教えてください。",
                 f"「{kanji_data['kanji']}」の意味は「{', '.join(kanji_data.get('meanings', []))}」です。"),
                
                (f"「{kanji_data['kanji']}」を使った例文を教えてください。",
                 self._generate_example_sentence(kanji_data)),
                
                (f"「{kanji_data['kanji']}」の画数は何画ですか？",
                 f"「{kanji_data['kanji']}」の画数は{kanji_data.get('stroke_count', 0)}画です。"),
                
                (f"「{kanji_data['kanji']}」は何年生で習う漢字ですか？",
                 f"「{kanji_data['kanji']}」は小学{grade}年生で習う漢字です。")
            ]
            
            question, answer = random.choice(question_patterns)
            
            sample = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer}
                ],
                "kanji": kanji_data['kanji'],
                "grade": grade
            }
            
            samples.append(sample)
        
        return Dataset.from_list(samples)
    
    def export_to_jsonl(self, dataset: Dataset, output_path: str):
        """データセットをJSONL形式でエクスポート"""
        with open(output_path, 'w', encoding='utf-8') as f:
            for sample in dataset:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    def export_to_parquet(self, dataset: Dataset, output_path: str):
        """データセットをParquet形式でエクスポート（Hugging Face推奨）"""
        dataset.to_parquet(output_path)
    
    def _grade_to_difficulty(self, grade: int) -> str:
        """学年を難易度に変換"""
        if grade <= 2:
            return "beginner"
        elif grade <= 4:
            return "intermediate"
        elif grade <= 6:
            return "advanced"
        else:
            return "native"
    
    def _generate_example_sentence(self, kanji_data) -> str:
        """漢字を使った例文を生成"""
        if kanji_data.get("example_words"):
            word, reading, _ = random.choice(kanji_data["example_words"])
            return f"例えば、「{word}」（{reading}）のように使います。"
        else:
            meanings = kanji_data.get("meanings", [])
            if meanings:
                return f"「{kanji_data['kanji']}」は{', '.join(meanings)}という意味で使われます。"
            else:
                return f"「{kanji_data['kanji']}」という漢字です。"
    
    def _generate_thinking_process(self, kanji: str, reading_type: str, reading: str, meanings: list, grade: int) -> str:
        """タスクに応じた思考過程を生成（タグなし）"""
        
        # 学年に応じた説明レベルを調整
        grade_name = f"小学{grade}年生" if grade <= 6 else "中学生"
        
        if reading_type == 'on_yomi':
            thinking_parts = [
                f"この漢字は「{kanji}」です。",
                f"{grade_name}で習う漢字です。"
            ]
            if meanings:
                thinking_parts.append(f"意味は「{', '.join(meanings[:2])}」などです。")
            thinking_parts.append(f"音読み（おんよみ）は中国から伝わった読み方です。")
            # 音読みの場合はひらがなに変換して表示
            reading_display = self._katakana_to_hiragana(reading) if reading_type == 'on_yomi' else reading
            thinking_parts.append(f"この漢字の音読みは「{reading_display}」です。")
            
        elif reading_type == 'kun_yomi':
            thinking_parts = [
                f"この漢字は「{kanji}」です。",
                f"{grade_name}で習う漢字です。"
            ]
            if meanings:
                thinking_parts.append(f"意味は「{', '.join(meanings[:2])}」などです。")
            thinking_parts.append(f"訓読み（くんよみ）は日本語の読み方です。")
            thinking_parts.append(f"この漢字の訓読みは「{reading}」です。")
            
        elif reading_type == 'writing':
            thinking_parts = [
                f"「{reading}」を漢字で書く問題です。",
                f"これは{grade_name}で習う漢字です。"
            ]
            if meanings:
                thinking_parts.append(f"意味は「{', '.join(meanings[:2])}」などです。")
            thinking_parts.append(f"「{reading}」は「{kanji}」と書きます。")
            
        else:
            # デフォルトの思考過程
            thinking_parts = [
                f"この問題について考えます。",
                f"答えは「{reading}」です。"
            ]
        
        return " ".join(thinking_parts)


# 使用例
if __name__ == "__main__":
    builder = HuggingFaceDatasetBuilder()
    
    # 1. 基本的な漢字読みデータセット
    kanji_dataset = builder.create_kanji_reading_dataset(
        num_samples_per_grade=100,
        grades=[1, 2],
        include_on_yomi=True,
        include_kun_yomi=True
    )
    
    print("Dataset statistics:")
    print(f"Train samples: {len(kanji_dataset['train'])}")
    print(f"Validation samples: {len(kanji_dataset['validation'])}")
    print(f"Test samples: {len(kanji_dataset['test'])}")
    
    # 2. GRPO用グループデータセット
    grpo_dataset = builder.create_grpo_dataset(
        num_groups=100,
        group_size=4
    )
    
    print(f"\nGRPO dataset samples: {len(grpo_dataset)}")
    
    # 3. チャット形式データセット
    chat_dataset = builder.create_chat_format_dataset(
        num_samples=500
    )
    
    print(f"\nChat dataset samples: {len(chat_dataset)}")
    
    # エクスポート例
    # builder.export_to_jsonl(kanji_dataset['train'], 'kanji_train.jsonl')
    # builder.export_to_parquet(kanji_dataset['train'], 'kanji_train.parquet')