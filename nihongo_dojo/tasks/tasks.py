"""
Japanese language tasks for GRPO training
"""

import random
import uuid
from typing import List, Dict, Optional, Tuple
from ..core import JapaneseTask, TaskType, TaskDifficulty
from .complete_kanji_tasks import CompleteKanjiTask
from .sample_augmentation import TaskSampleAugmenter


class KanjiTask:
    """漢字関連のタスク生成"""
    
    def __init__(self):
        self.kanji_data = {
            TaskDifficulty.BEGINNER: {
                "読み": [
                    ("人", "ひと", "person"),
                    ("日本", "にほん", "Japan"),
                    ("学生", "がくせい", "student"),
                    ("先生", "せんせい", "teacher"),
                    ("友達", "ともだち", "friend"),
                    ("家族", "かぞく", "family"),
                    ("時間", "じかん", "time"),
                    ("毎日", "まいにち", "every day")
                ],
                "書き": [
                    ("きょう", "今日", "today"),
                    ("あした", "明日", "tomorrow"),
                    ("がっこう", "学校", "school"),
                    ("でんしゃ", "電車", "train"),
                    ("ほん", "本", "book"),
                    ("みず", "水", "water")
                ]
            },
            TaskDifficulty.INTERMEDIATE: {
                "読み": [
                    ("経済", "けいざい", "economy"),
                    ("社会", "しゃかい", "society"),
                    ("政治", "せいじ", "politics"),
                    ("環境", "かんきょう", "environment"),
                    ("技術", "ぎじゅつ", "technology"),
                    ("文化", "ぶんか", "culture")
                ],
                "書き": [
                    ("けんきゅう", "研究", "research"),
                    ("かいぎ", "会議", "meeting"),
                    ("れんらく", "連絡", "contact"),
                    ("よやく", "予約", "reservation")
                ]
            },
            TaskDifficulty.ADVANCED: {
                "読み": [
                    ("曖昧", "あいまい", "ambiguous"),
                    ("躊躇", "ちゅうちょ", "hesitation"),
                    ("矛盾", "むじゅん", "contradiction"),
                    ("概念", "がいねん", "concept"),
                    ("抽象", "ちゅうしょう", "abstract")
                ],
                "書き": [
                    ("ふくざつ", "複雑", "complex"),
                    ("こうりつ", "効率", "efficiency"),
                    ("せきにん", "責任", "responsibility")
                ]
            }
        }
    
    def generate_reading_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """漢字読みタスクを生成"""
        kanji_list = self.kanji_data.get(difficulty, {}).get("読み", [])
        if not kanji_list:
            kanji_list = self.kanji_data[TaskDifficulty.BEGINNER]["読み"]
        
        kanji, reading, meaning = random.choice(kanji_list)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KANJI_READING,
            difficulty=difficulty,
            instruction="次の漢字の読み方をひらがなで答えてください。",
            context=None,
            question=f"「{kanji}」の読み方は？",
            answer=reading,
            explanation=f"「{kanji}」は「{reading}」と読みます。意味: {meaning}",
            metadata={"meaning": meaning}
        )
    
    def generate_writing_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """漢字書きタスクを生成"""
        kanji_list = self.kanji_data.get(difficulty, {}).get("書き", [])
        if not kanji_list:
            kanji_list = self.kanji_data[TaskDifficulty.BEGINNER]["書き"]
        
        reading, kanji, meaning = random.choice(kanji_list)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KANJI_WRITING,
            difficulty=difficulty,
            instruction="次のひらがなを漢字で書いてください。",
            context=None,
            question=f"「{reading}」を漢字で書くと？",
            answer=kanji,
            explanation=f"「{reading}」は「{kanji}」と書きます。意味: {meaning}",
            metadata={"meaning": meaning}
        )



class ParticleTask:
    """助詞穴埋めタスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.particle_examples = TaskSampleAugmenter.get_augmented_particle_examples()
    
    def generate_particle_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """助詞穴埋めタスクを生成"""
        examples = self.particle_examples.get(difficulty, self.particle_examples[TaskDifficulty.BEGINNER])
        sentence, particles, explanation = random.choice(examples)
        
        # 問題文を作成（下線部分を[　]に変換）
        question = sentence.replace("＿", "[　]")
        
        # 助詞が1つの場合は文字列、複数の場合はリストとして返す
        answer = particles[0] if len(particles) == 1 else particles
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.PARTICLE_FILL,
            difficulty=difficulty,
            instruction="文中の[　]に入る適切な助詞を答えてください。",
            context=None,
            question=question,
            answer=answer,
            explanation=f"この文では{explanation}を表す助詞を使います。",
            metadata={"particle_count": len(particles)}
        )


class KeigoTask:
    """敬語変換タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.keigo_examples = TaskSampleAugmenter.get_augmented_keigo_examples()
    
    def generate_keigo_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """敬語変換タスクを生成"""
        examples = self.keigo_examples.get(difficulty, self.keigo_examples[TaskDifficulty.INTERMEDIATE])
        verb_data = random.choice(examples)
        
        # ランダムに敬語タイプを選択
        keigo_types = ["sonkeigo", "kenjougo"]
        selected_type = random.choice(keigo_types)
        
        type_name = {
            "sonkeigo": "尊敬語",
            "kenjougo": "謙譲語"
        }[selected_type]
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.KEIGO_CONVERSION,
            difficulty=difficulty,
            instruction=f"次の動詞を{type_name}に変換してください。",
            context=None,
            question=f"「{verb_data['plain']}」の{type_name}は？",
            answer=verb_data[selected_type],
            explanation=f"「{verb_data['plain']}」の{type_name}は「{verb_data[selected_type]}」です。",
            metadata={
                "keigo_type": selected_type,
                "all_forms": verb_data
            }
        )


class WordOrderTask:
    """語順並び替えタスク"""
    
    def __init__(self):
        # 増幅されたデータを変換
        augmented_data = TaskSampleAugmenter.get_augmented_word_order_examples()
        self.word_order_examples = {}
        
        for difficulty, examples in augmented_data.items():
            self.word_order_examples[difficulty] = []
            for words, description in examples:
                self.word_order_examples[difficulty].append({
                    "words": words,
                    "correct": "".join(words),
                    "meaning": description
                })
            
    
    def generate_word_order_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """語順並び替えタスクを生成"""
        examples = self.word_order_examples.get(difficulty, self.word_order_examples[TaskDifficulty.BEGINNER])
        example = random.choice(examples)
        
        # 単語をシャッフル
        shuffled = example["words"].copy()
        random.shuffle(shuffled)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.WORD_ORDER,
            difficulty=difficulty,
            instruction="次の単語を正しい順番に並び替えて文を作ってください。",
            context=f"意味: {example['meaning']}",
            question=" / ".join(shuffled),
            answer=example["correct"],
            explanation=f"正しい語順は「{example['correct']}」です。",
            metadata={"word_count": len(example["words"]), "meaning": example["meaning"]}
        )


class CounterWordTask:
    """助数詞タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        augmented_counters = TaskSampleAugmenter.get_augmented_counter_examples()
        self.counter_examples = {}
        
        # 助数詞と対応する物品のマッピング
        self.counter_to_items = {
            "人": ["人", "学生", "先生", "友達", "子供"],
            "本": ["鉛筆", "ペン", "箸", "木", "線"],
            "枚": ["紙", "写真", "お皿", "シャツ", "チケット"],
            "個": ["りんご", "ボール", "石", "卵", "パン"],
            "冊": ["本", "雑誌", "辞書", "ノート", "漫画"],
            "台": ["車", "機械", "テレビ", "パソコン", "自転車"],
            "匹": ["犬", "猫", "魚", "鳥", "馬"],
            "つ": ["机", "椅子", "かばん", "時計", "カメラ"],
            "杯": ["コーヒー", "お茶", "ジュース", "ビール", "水"],
            "回": ["授業", "会議", "試験", "練習", "旅行"],
            "軒": ["家", "店", "病院", "学校", "工場"],
            "頭": ["牛", "象", "ライオン", "トラ", "熊"],
            "羽": ["鳥", "鶏", "鴨", "鳩", "すずめ"],
            "足": ["靴", "靴下", "スリッパ", "下駄", "ブーツ"],
            "階": ["階", "フロア", "段階", "レベル", "層"],
            "番": ["番号", "順番", "チャンネル", "問題", "席"],
            "組": ["組", "ペア", "チーム", "グループ", "セット"],
            "通": ["手紙", "メール", "はがき", "招待状", "通知"]
        }
        
        # 各難易度のデータを整理
        for difficulty, counter_list in augmented_counters.items():
            self.counter_examples[difficulty] = []
            for counter_type, examples in counter_list:
                # 助数詞に対応する物品を取得
                items = self.counter_to_items.get(counter_type, [counter_type])
                reading = examples[0][1].split(counter_type)[1] if counter_type in examples[0][1] else counter_type
                description = f"{counter_type}を使う物品"
                self.counter_examples[difficulty].append((counter_type, reading, items, description))
    
    def generate_counter_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """助数詞タスクを生成"""
        examples = self.counter_examples.get(difficulty, self.counter_examples[TaskDifficulty.BEGINNER])
        counter, reading, items, category = random.choice(examples)
        
        # ランダムに数字を選択
        number = random.randint(1, 10)
        item = random.choice(items)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.COUNTER_WORD,
            difficulty=difficulty,
            instruction="適切な助数詞を使って数えてください。",
            context=None,
            question=f"{item}が{number}つあります。正しい数え方は？",
            answer=f"{number}{counter}",
            explanation=f"{item}のような物を数えるときは「{counter}（{reading}）」を使います。",
            metadata={
                "counter": counter,
                "reading": reading,
                "category": category,
                "number": number,
                "item": item
            }
        )



