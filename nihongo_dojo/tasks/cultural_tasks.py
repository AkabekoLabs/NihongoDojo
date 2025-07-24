"""
Japanese cultural and contextual tasks
日本文化・文脈理解タスク
"""

import random
import uuid
from typing import List, Dict, Optional
from ..core import JapaneseTask, TaskType, TaskDifficulty
from .advanced_sample_augmentation import AdvancedTaskSampleAugmenter


class SeasonalExpressionTask:
    """季節の挨拶・表現タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.seasonal_data = AdvancedTaskSampleAugmenter.get_augmented_seasonal_expression_examples()
    
    def generate_seasonal_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """季節の挨拶タスク生成"""
        season = random.choice(list(self.seasonal_data.keys()))
        expressions = self.seasonal_data[season]  # これはlistです
        
        # listから1つの表現を選択
        expression = random.choice(expressions)
        
        # 季節名のマッピング
        season_names = {
            "spring": "春",
            "summer": "夏",
            "autumn": "秋",
            "winter": "冬"
        }
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.SEASONAL_EXPRESSION,
            difficulty=difficulty,
            instruction="次の場面に適した季節の表現を答えてください。",
            context=f"{expression['context']} ({expression['usage']})",
            question=f"{season_names.get(season, season)}の表現として適切なものは？",
            answer=expression['expression'],
            explanation=f"読み: {expression.get('reading', '')}",
            metadata={
                "season": season,
                "context": expression['context']
            }
        )


class HonorificsTask:
    """敬語・謙譲語・丁寧語の総合タスク"""
    
    def __init__(self):
        self.honorifics_situations = {
            # 場面別敬語
            "customer_service": {
                "situation": "店員がお客様に対して",
                "examples": [
                    {
                        "plain": "何を探していますか？",
                        "polite": "何をお探しでしょうか？",
                        "very_polite": "何かお探しのものはございますか？",
                        "explanation": "お客様に対しては最上級の敬語を使用"
                    },
                    {
                        "plain": "これはどうですか？",
                        "polite": "こちらはいかがですか？",
                        "very_polite": "こちらはいかがでございますか？",
                        "explanation": "商品を勧める際の表現"
                    }
                ]
            },
            "job_interview": {
                "situation": "就職面接で",
                "examples": [
                    {
                        "plain": "大学で経済を勉強しました",
                        "polite": "大学で経済を勉強しました",
                        "formal": "大学で経済を専攻しておりました",
                        "explanation": "自分の行動には謙譲語を使用"
                    },
                    {
                        "plain": "質問があります",
                        "polite": "質問があります",
                        "formal": "お伺いしたいことがございます",
                        "explanation": "質問する際の謙譲表現"
                    }
                ]
            },
            "email_to_superior": {
                "situation": "上司へのメール",
                "examples": [
                    {
                        "plain": "確認してください",
                        "polite": "確認をお願いします",
                        "formal": "ご確認いただけますでしょうか",
                        "explanation": "依頼の際は疑問形で丁寧に"
                    },
                    {
                        "plain": "資料を見ました",
                        "polite": "資料を見ました",
                        "formal": "資料を拝見いたしました",
                        "explanation": "「見る」の謙譲語は「拝見する」"
                    }
                ]
            }
        }
        
        # 間違いやすい敬語
        self.common_mistakes = [
            {
                "wrong": "お座りください",
                "correct": "お掛けください",
                "explanation": "「座る」の尊敬語は「お掛けになる」"
            },
            {
                "wrong": "ご苦労様でした",
                "correct": "お疲れ様でした",
                "explanation": "「ご苦労様」は目上から目下への言葉"
            },
            {
                "wrong": "了解しました",
                "correct": "承知いたしました",
                "explanation": "ビジネスでは「承知」を使う"
            },
            {
                "wrong": "すみません",
                "correct": "申し訳ございません",
                "explanation": "正式な謝罪では「申し訳ございません」"
            }
        ]
    
    def generate_honorifics_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """敬語タスク生成"""
        task_type = random.choice(["situation", "correction"])
        
        if task_type == "situation":
            situation_key = random.choice(list(self.honorifics_situations.keys()))
            situation = self.honorifics_situations[situation_key]
            example = random.choice(situation["examples"])
            
            level = "formal" if difficulty == TaskDifficulty.ADVANCED else "polite"
            if "very_polite" in example and difficulty == TaskDifficulty.ADVANCED:
                level = "very_polite"
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.KEIGO_CONVERSION,
                difficulty=difficulty,
                instruction=f"{situation['situation']}使う適切な敬語表現に変換してください。",
                context=situation['situation'],
                question=example['plain'],
                answer=example[level],
                explanation=example['explanation'],
                metadata={
                    "situation": situation_key,
                    "formality_level": level
                }
            )
        
        else:  # correction
            mistake = random.choice(self.common_mistakes)
            
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.HONORIFICS,
                difficulty=difficulty,
                instruction="間違った敬語表現を正しく直してください。",
                context="ビジネスシーンでの敬語",
                question=mistake['wrong'],
                answer=mistake['correct'],
                explanation=mistake['explanation'],
                metadata={"error_type": "honorifics"}
            )


class SocialContextTask:
    """社会的文脈・場面理解タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.social_situations = AdvancedTaskSampleAugmenter.get_augmented_social_context_examples()
    
    def generate_social_context_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """社会的文脈タスク生成"""
        category = random.choice(list(self.social_situations.keys()))
        situations = self.social_situations[category]  # これはlistです
        
        # listから1つのシチュエーションを選択
        situation = random.choice(situations)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.SOCIAL_CONTEXT,
            difficulty=difficulty,
            instruction="次の場面で使う適切な表現を答えてください。",
            context=situation.get('occasion', situation.get('context', category)),
            question="この場面での適切な表現は？",
            answer=situation.get('phrase', situation.get('expression', '')),
            explanation=situation.get('meaning', situation.get('explanation', '')),
            metadata={
                "category": category,
                "response": situation.get('response', '')
            }
        )


class RegionalDialectTask:
    """方言・地域言語タスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.dialects = AdvancedTaskSampleAugmenter.get_augmented_regional_dialect_examples()
    
    def generate_dialect_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """方言タスク生成"""
        dialect_key = random.choice(list(self.dialects.keys()))
        dialect_examples = self.dialects[dialect_key]  # これはlistです
        example = random.choice(dialect_examples)
        
        # 方言名のマッピング
        dialect_names = {
            "kansai": "関西弁",
            "kyushu": "九州弁",
            "tohoku": "東北弁",
            "okinawa": "沖縄方言"
        }
        
        # 地域のマッピング
        dialect_regions = {
            "kansai": "関西地方",
            "kyushu": "九州地方",
            "tohoku": "東北地方",
            "okinawa": "沖縄県"
        }
        
        dialect_name = dialect_names.get(dialect_key, dialect_key)
        dialect_region = dialect_regions.get(dialect_key, "日本")
        
        # 難易度に応じてタスクを変える
        if difficulty == TaskDifficulty.BEGINNER:
            # 標準語から方言へ
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.REGIONAL_DIALECT,
                difficulty=difficulty,
                instruction=f"次の標準語を{dialect_name}に変換してください。",
                context=f"意味: {example.get('meaning', '')}",
                question=example['standard'],
                answer=example['dialect'],
                explanation=f"{dialect_name}は{dialect_region}で話されています。",
                metadata={
                    "dialect": dialect_key,
                    "direction": "to_dialect"
                }
            )
        else:
            # 方言から標準語へ
            return JapaneseTask(
                id=str(uuid.uuid4()),
                type=TaskType.REGIONAL_DIALECT,
                difficulty=difficulty,
                instruction=f"次の{dialect_name}を標準語に変換してください。",
                context=f"意味: {example.get('meaning', '')}",
                question=example['dialect'],
                answer=example['standard'],
                explanation=f"「{example['dialect']}」は{dialect_name}の表現です。",
                metadata={
                    "dialect": dialect_key,
                    "direction": "to_standard"
                }
            )


class AgeGenderLanguageTask:
    """年齢・性別による言葉遣いタスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.language_variations = AdvancedTaskSampleAugmenter.get_augmented_age_gender_language_examples()
    
    def generate_age_gender_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """年齢・性別言語タスク生成"""
        category = random.choice(list(self.language_variations.keys()))
        variations = self.language_variations[category]  # これはlistです
        variation = random.choice(variations)
        
        # カテゴリーごとの説明
        category_descriptions = {
            "feminine": "女性的な表現",
            "masculine": "男性的な表現",
            "youth": "若者言葉",
            "elderly": "年配の方の言葉",
            "children": "子供の言葉",
            "formal": "フォーマルな表現"
        }
        
        description = category_descriptions.get(category, category)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.AGE_GENDER_LANGUAGE,
            difficulty=difficulty,
            instruction=f"次の表現は{description}の例です。どのような場面で使われるか説明してください。",
            context=f"表現タイプ: {description}",
            question=variation.get('example', variation.get('expression', '')),
            answer=variation.get('meaning', ''),
            explanation=f"フォーマリティ: {variation.get('formality', 'standard')}",
            metadata={
                "language_variety": category,
                "expression": variation.get('expression', ''),
                "formality": variation.get('formality', '')
            }
        )


class EmotionalExpressionTask:
    """感情表現・ニュアンスタスク"""
    
    def __init__(self):
        # 増幅されたデータを使用
        self.emotions = AdvancedTaskSampleAugmenter.get_augmented_emotional_expression_examples()
    
    def generate_emotion_task(self, difficulty: TaskDifficulty) -> JapaneseTask:
        """感情表現タスク生成"""
        emotion_type = random.choice(list(self.emotions.keys()))
        expressions = self.emotions[emotion_type]  # これはlistです
        expression = random.choice(expressions)
        
        # 感情タイプの日本語名
        emotion_names = {
            "happiness": "喜び",
            "sadness": "悲しみ",
            "anger": "怒り",
            "fear": "恐れ",
            "surprise": "驚き",
            "gratitude": "感謝",
            "apology": "謝罪",
            "frustration": "苛立ち",
            "disappointment": "失望"
        }
        
        emotion_name = emotion_names.get(emotion_type, emotion_type)
        
        return JapaneseTask(
            id=str(uuid.uuid4()),
            type=TaskType.EMOTIONAL_EXPRESSION,
            difficulty=difficulty,
            instruction=f"次の場面での{emotion_name}の表現として適切なものを答えてください。",
            context=expression.get('context', ''),
            question=f"この状況での{emotion_name}の表現は？",
            answer=expression['expression'],
            explanation=f"感情の強さ: {expression.get('level', 'normal')}",
            metadata={
                "emotion_type": emotion_type,
                "level": expression.get('level', ''),
                "example": expression.get('example', '')
            }
        )