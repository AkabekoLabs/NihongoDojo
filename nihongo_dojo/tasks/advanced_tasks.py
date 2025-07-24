"""
Advanced Japanese language tasks for GRPO training
拡張された日本語タスク集
"""

import random
import uuid
from typing import List, Dict, Optional, Tuple
from ..core import JapaneseTask, TaskType, TaskDifficulty
from .advanced_sample_augmentation import AdvancedTaskSampleAugmenter


class AdvancedGrammarTask:
    """高度な文法パターンのタスク"""
    
    def __init__(self):
        self.grammar_patterns = {
            # 〜ば〜ほど（the more...the more）
            "conditional_progressive": {
                "pattern": "〜ば〜ほど",
                "examples": [
                    {
                        "base": "勉強する",
                        "sentence": "勉強すればするほど、成績が良くなります。",
                        "meaning": "The more you study, the better your grades become."
                    },
                    {
                        "base": "練習する",
                        "sentence": "練習すればするほど、上手になります。",
                        "meaning": "The more you practice, the better you become."
                    }
                ]
            },
            # 〜にもかかわらず（despite/in spite of）
            "contrast": {
                "pattern": "〜にもかかわらず",
                "examples": [
                    {
                        "base": "雨が降っている",
                        "sentence": "雨が降っているにもかかわらず、試合は続行された。",
                        "meaning": "Despite the rain, the match continued."
                    }
                ]
            },
            # 〜ことになっている（it is decided/supposed to）
            "decision_state": {
                "pattern": "〜ことになっている",
                "examples": [
                    {
                        "base": "会議は3時に始まる",
                        "sentence": "会議は3時に始まることになっています。",
                        "meaning": "The meeting is scheduled to start at 3."
                    }
                ]
            },
            # 〜ようになる（come to/become able to）
            "change_state": {
                "pattern": "〜ようになる",
                "examples": [
                    {
                        "base": "日本語が話せる",
                        "sentence": "日本語が話せるようになりました。",
                        "meaning": "I became able to speak Japanese."
                    }
                ]
            },
            # 〜たばかり（just did）
            "just_completed": {
                "pattern": "〜たばかり",
                "examples": [
                    {
                        "base": "食べる",
                        "sentence": "昼ご飯を食べたばかりです。",
                        "meaning": "I just ate lunch."
                    }
                ]
            },
            # 〜てばかりいる（always/only doing）
            "continuous_only": {
                "pattern": "〜てばかりいる",
                "examples": [
                    {
                        "base": "遊ぶ",
                        "sentence": "彼は遊んでばかりいる。",
                        "meaning": "He is always playing around."
                    }
                ]
            },
            # 〜ないことはない（it's not that...not）
            "double_negative": {
                "pattern": "〜ないことはない",
                "examples": [
                    {
                        "base": "分かる",
                        "sentence": "分からないことはないが、難しい。",
                        "meaning": "It's not that I don't understand, but it's difficult."
                    }
                ]
            },
            # 〜というわけではない（it doesn't mean that）
            "clarification": {
                "pattern": "〜というわけではない",
                "examples": [
                    {
                        "base": "嫌い",
                        "sentence": "嫌いというわけではないが、苦手だ。",
                        "meaning": "It's not that I dislike it, but I'm not good at it."
                    }
                ]
            }
        }
    
    def generate_pattern_transformation_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """文法パターン変換タスク"""
        pattern_keys = list(self.grammar_patterns.keys())
        pattern_key = random.choice(pattern_keys)
        pattern_data = self.grammar_patterns[pattern_key]
        
        example = random.choice(pattern_data["examples"])
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.ADVANCED_GRAMMAR,
            difficulty=difficulty,
            instruction=f"次の文を「{pattern_data['pattern']}」を使って書き換えてください。",
            context=f"意味: {example['meaning']}",
            question=example['base'],
            answer=example['sentence'],
            explanation=f"「{pattern_data['pattern']}」は{example['meaning']}という意味を表します。",
            metadata={
                "pattern": pattern_data['pattern'],
                "pattern_type": pattern_key
            }
        )


class OnomatopoeiaTask:
    """擬音語・擬態語タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        augmented_data = AdvancedTaskSampleAugmenter.get_augmented_onomatopoeia_examples()
        
        # データフォーマットを変換
        self.onomatopoeia_data = {}
        for category, examples in augmented_data.items():
            self.onomatopoeia_data[category] = []
            for word, context, english in examples:
                # 例文を生成
                if category == "giongo":
                    example = f"{word}という音が聞こえる。"
                elif category == "gitaigo":
                    example = f"{word}している。"
                elif category == "gijougo":
                    example = f"気持ちが{word}する。"
                else:  # giseigo
                    example = f"{word}と声を出す。"
                
                self.onomatopoeia_data[category].append({
                    "word": word,
                    "reading": word.lower(),  # カタカナをひらがなに（簡易的に）
                    "meaning": english,
                    "example": example,
                    "context": context
                })
    
    def generate_onomatopoeia_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """擬音語・擬態語の使い方タスク"""
        category = random.choice(["giongo", "gitaigo", "gijougo"])
        word_data = random.choice(self.onomatopoeia_data[category])
        
        # 空欄補充形式
        sentence_with_blank = word_data['example'].replace(word_data['word'], "（　　）")
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.PARTICLE_FILL,  # 使い回しですが、新しいタスクタイプを作ることもできます
            difficulty=difficulty,
            instruction="文中の（　　）に入る適切な擬音語・擬態語を答えてください。",
            context=word_data['context'],
            question=sentence_with_blank,
            answer=word_data['word'],
            explanation=f"「{word_data['word']}」は{word_data['meaning']}を表す{'擬音語' if category == 'giongo' else '擬態語' if category == 'gitaigo' else '擬情語'}です。",
            metadata={
                "category": category,
                "reading": word_data['reading']
            }
        )


class ConversationTask:
    """会話・対話タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.conversation_patterns = AdvancedTaskSampleAugmenter.get_augmented_conversation_examples()
    
    def generate_conversation_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """会話タスクを生成"""
        task_type = random.choice(["aizuchi", "requests", "refusals", "phone"])
        
        if task_type == "aizuchi":
            pattern = random.choice(self.conversation_patterns["aizuchi"])
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.CONVERSATION,
                difficulty=difficulty,
                instruction="次の状況で適切なあいづちを選んでください。",
                context=pattern['context'],
                question="適切な応答は？",
                answer=random.choice(pattern['responses']),
                explanation=f"この状況では共感や関心を示すあいづちが適切です。",
                metadata={
                    "conversation_type": "aizuchi",
                    "all_appropriate": pattern['responses'],
                    "formal_responses": pattern.get('formal_responses', [])
                }
            )
        
        elif task_type == "requests":
            pattern = random.choice(self.conversation_patterns["requests"])
            formality = "polite" if difficulty in [TaskDifficulty.INTERMEDIATE, TaskDifficulty.ADVANCED] else "casual"
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.CONVERSATION,
                difficulty=difficulty,
                instruction=f"次の状況で{'丁寧な' if formality == 'polite' else 'カジュアルな'}依頼表現を作ってください。",
                context=pattern['situation'],
                question="どのように依頼しますか？",
                answer=pattern[formality],
                explanation=f"{'ビジネスシーンでは丁寧な表現が必要です。' if formality == 'polite' else '友達なのでカジュアルな表現で大丈夫です。'}",
                metadata={
                    "conversation_type": "request",
                    "formality": formality
                }
            )


class ProverbIdiomTask:
    """ことわざ・慣用句タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        augmented_data = AdvancedTaskSampleAugmenter.get_augmented_proverb_idiom_examples()
        
        # ことわざを難易度別に整理
        self.proverbs = {
            TaskDifficulty.BEGINNER: augmented_data["proverbs"][:4],
            TaskDifficulty.INTERMEDIATE: augmented_data["proverbs"][4:8],
            TaskDifficulty.ADVANCED: augmented_data["proverbs"][8:]
        }
        
        # 慣用句とその他のデータを格納
        self.idioms = {
            "body_parts": augmented_data["idioms"],
            "yojijukugo": augmented_data.get("yojijukugo", [])
        }
    
    def generate_proverb_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """ことわざタスク生成"""
        proverbs = self.proverbs.get(difficulty, self.proverbs[TaskDifficulty.BEGINNER])
        proverb_data = random.choice(proverbs)
        
        task_variant = random.choice(["meaning", "usage", "complete"])
        
        if task_variant == "meaning":
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.PROVERB_IDIOM,
                difficulty=difficulty,
                instruction="次のことわざの意味を説明してください。",
                context=None,
                question=f"「{proverb_data['proverb']}」の意味は？",
                answer=proverb_data['meaning'],
                explanation=f"使用場面: {proverb_data['usage']}",
                metadata={"proverb_type": "kotowaza", "reading": proverb_data['reading']}
            )
        
        elif task_variant == "complete":
            # ことわざの一部を空欄にする
            words = proverb_data['proverb'].split('も')
            if len(words) > 1:
                question = f"{words[0]}も（　　）"
                answer = 'も'.join(words[1:])
            else:
                question = proverb_data['proverb'][:2] + "（　　）"
                answer = proverb_data['proverb'][2:]
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.PARTICLE_FILL,
                difficulty=difficulty,
                instruction="ことわざを完成させてください。",
                context=f"意味: {proverb_data['meaning']}",
                question=question,
                answer=answer,
                explanation=f"「{proverb_data['proverb']}」: {proverb_data['meaning']}",
                metadata={"proverb_type": "completion"}
            )


class BusinessJapaneseTask:
    """ビジネス日本語タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.business_expressions = AdvancedTaskSampleAugmenter.get_augmented_business_japanese_examples()
    
    def generate_business_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """ビジネス日本語タスク生成"""
        category = random.choice(["email", "presentation", "meeting"])
        
        if category == "email":
            task_type = random.choice(["openings", "closings", "phrases"])
            expressions = self.business_expressions["email"][task_type]
            expression = random.choice(expressions)
            
            context_map = {
                "openings": "ビジネスメールの書き出し",
                "closings": "ビジネスメールの締めくくり",
                "phrases": "ビジネスメールでよく使う表現"
            }
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.BUSINESS_JAPANESE,
                difficulty=difficulty,
                instruction=f"{context_map[task_type]}として適切な表現を選んでください。",
                context="ビジネスメール",
                question="適切な表現は？",
                answer=expression,
                explanation="ビジネスメールでは丁寧で形式的な表現を使います。",
                metadata={
                    "business_type": "email",
                    "part": task_type
                }
            )
        
        elif category == "meeting":
            # 新しいデータ構造に合わせて修正（agreement/disagreementに変更）
            subcategory = random.choice(["starting", "opinions", "agreement", "disagreement"])
            expressions = self.business_expressions["meeting"][subcategory]
            expression = random.choice(expressions)
            
            instruction_map = {
                "starting": "会議を始める時の表現",
                "opinions": "会議で意見を述べる時の表現",
                "agreement": "相手の意見に賛成する時の表現",
                "disagreement": "相手の意見に反対する時の表現"
            }
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.BUSINESS_JAPANESE,
                difficulty=difficulty,
                instruction=f"{instruction_map[subcategory]}を答えてください。",
                context="ビジネス会議の場面",
                question="適切な表現は？",
                answer=expression,
                explanation="会議では相手を尊重しながら意見を述べることが大切です。",
                metadata={
                    "business_type": "meeting",
                    "expression_type": subcategory
                }
            )


class ClassicalJapaneseTask:
    """古文・古典日本語タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        augmented_data = AdvancedTaskSampleAugmenter.get_augmented_classical_japanese_examples()
        self.classical_patterns = {
            "auxiliary_verbs": augmented_data["auxiliary_verbs"],
            "particles": augmented_data["particles"],
            "kakari_musubi": augmented_data.get("kakari_musubi", []),
            "famous_texts": augmented_data.get("famous_texts", []),
            "conjugations": augmented_data.get("conjugations", [])
        }
    
    def generate_classical_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """古文タスク生成"""
        task_type = random.choice(["translation", "particle", "auxiliary_verb"])
        
        if task_type == "translation":
            verb_data = random.choice(self.classical_patterns["auxiliary_verbs"])
            
            # 現代語→古文 or 古文→現代語をランダムに選択
            direction = random.choice(["to_classical", "to_modern"])
            
            if direction == "to_classical":
                return JapaneseTask(
                    id=str(uuid.uuid4()),
                    type=TaskType.CLASSICAL_JAPANESE,
                    difficulty=TaskDifficulty.ADVANCED,
                    instruction="次の現代語を古文に訳してください。",
                    context=f"助動詞「{verb_data['classical']}」を使用",
                    question=verb_data['translation'],
                    answer=verb_data['example'],
                    explanation=f"{verb_data['type']}を表す「{verb_data['classical']}」を使います。",
                    metadata={"classical_type": "translation", "direction": direction}
                )
            else:
                return JapaneseTask(
                    id=str(uuid.uuid4()),
                    type=TaskType.CLASSICAL_JAPANESE,
                    difficulty=TaskDifficulty.ADVANCED,
                    instruction="次の古文を現代語に訳してください。",
                    context=None,
                    question=verb_data['example'],
                    answer=verb_data['translation'],
                    explanation=f"「{verb_data['classical']}」は{verb_data['type']}を表します。",
                    metadata={"classical_type": "translation", "direction": direction}
                )
        
        elif task_type == "particle":
            particle_data = random.choice(self.classical_patterns["particles"])
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.ADVANCED_GRAMMAR,
                difficulty=TaskDifficulty.ADVANCED,
                instruction="次の古文の助詞の用法を説明してください。",
                context=particle_data['example'],
                question=f"「{particle_data['classical']}」の用法は？",
                answer=f"{particle_data['usage']}を表す",
                explanation=f"現代語では「{particle_data['modern']}」に相当します。",
                metadata={"classical_type": "particle", "usage": particle_data['usage']}
            )
        
        elif task_type == "auxiliary_verb":
            # 助動詞の活用形を問う
            verb_data = random.choice(self.classical_patterns["auxiliary_verbs"])
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.ADVANCED_GRAMMAR,
                difficulty=TaskDifficulty.ADVANCED,
                instruction="次の古典助動詞の意味を答えてください。",
                context=verb_data['example'],
                question=f"「{verb_data['classical']}」の意味は？",
                answer=verb_data['type'],
                explanation=f"「{verb_data['classical']}」は{verb_data['type']}を表す助動詞です。",
                metadata={"classical_type": "auxiliary_verb"}
            )


class SpecializedVocabularyTask:
    """専門用語・分野別語彙タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.specialized_vocab = AdvancedTaskSampleAugmenter.get_augmented_specialized_vocabulary_examples()
    
    def generate_vocabulary_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """専門用語タスク生成"""
        field = random.choice(list(self.specialized_vocab.keys()))
        term_data = random.choice(self.specialized_vocab[field])
        
        task_variant = random.choice(["definition", "usage", "translation"])
        
        if task_variant == "definition":
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.PROVERB_IDIOM,
                difficulty=difficulty,
                instruction="次の専門用語の意味を説明してください。",
                context=f"分野: {field}",
                question=f"「{term_data['term']}」とは？",
                answer=term_data['definition'],
                explanation=f"英語: {term_data['english']}",
                metadata={
                    "field": field,
                    "reading": term_data['reading']
                }
            )
        
        elif task_variant == "usage":
            # 読み方を問う問題
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.KANJI_READING,
                difficulty=difficulty,
                instruction="次の専門用語の読み方をひらがなで答えてください。",
                context=f"分野: {field}",
                question=f"「{term_data['term']}」の読み方は？",
                answer=term_data['reading'],
                explanation=f"意味: {term_data['definition']}",
                metadata={"field": field}
            )
        
        elif task_variant == "translation":
            # 英語から日本語の専門用語を答える
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.SPECIALIZED_VOCABULARY,
                difficulty=difficulty,
                instruction="次の英語の専門用語を日本語で答えてください。",
                context=f"分野: {field}",
                question=term_data['english'],
                answer=term_data['term'],
                explanation=f"読み: {term_data['reading']}、意味: {term_data['definition']}",
                metadata={"field": field}
            )