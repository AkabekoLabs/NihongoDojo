"""
助数詞（カウンター）タスク専用の改良版報酬関数
"""

import re
from typing import List, Dict, Any, Optional


class CounterRewardFunctions:
    """助数詞タスク用の改良された報酬関数"""
    
    def __init__(self, reasoning_start="<reasoning>", reasoning_end="</reasoning>",
                 solution_start="<answer>", solution_end="</answer>", 
                 eos_token=""):
        self.reasoning_start = reasoning_start
        self.reasoning_end = reasoning_end
        self.solution_start = solution_start
        self.solution_end = solution_end
        self.eos_token = eos_token
        
        # 正規表現パターンを作成
        self._create_regex_pattern()
        
        # カウンターのカテゴリー定義
        self.COUNTER_CATEGORIES = {
            "animals_small": ["匹"],  # 小動物
            "animals_large": ["頭"],  # 大型動物
            "birds": ["羽"],          # 鳥類
            "people": ["人", "名"],   # 人
            "flat_objects": ["枚"],   # 平たいもの
            "bound_objects": ["冊", "巻"],  # 本・巻物
            "long_objects": ["本"],   # 長いもの
            "vehicles": ["台"],       # 乗り物・機械
            "small_objects": ["個", "つ"],  # 小さいもの・一般
            "buildings": ["軒", "棟", "戸"],  # 建物
            "floors": ["階"],         # 階数
            "letters": ["通"],        # 手紙・文書
            "pairs": ["足", "対"],    # 対のもの
            "sets": ["組", "セット"], # セット
            "times": ["回", "度"],    # 回数
            "order": ["番", "位"],    # 順序
        }
        
        # カテゴリー逆引き辞書
        self.counter_to_category = {}
        for category, counters in self.COUNTER_CATEGORIES.items():
            for counter in counters:
                self.counter_to_category[counter] = category
    
    def _create_regex_pattern(self):
        """フォーマット確認用の正規表現パターンを作成"""
        solution_end_regex = r"</answer>[\s]{0,}"
        if self.eos_token:
            solution_end_regex += "(?:" + re.escape(self.eos_token) + ")?"
        
        self.match_format = re.compile(
            rf"{self.reasoning_end}.*?"
            rf"{self.solution_start}(.+?){solution_end_regex}"
            rf"[\s]{{0,}}$",
            flags=re.MULTILINE | re.DOTALL
        )
    
    def balanced_check_counter(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """バランスの取れた助数詞チェック（厳格化版）"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            # answerがフルソリューション形式の場合、実際の答えを抽出
            if answer and len(answer) > 0 and isinstance(answer[0], str) and '<answer>' in answer[0]:
                extracted_answers = []
                for ans in answer:
                    match = re.search(r'<answer>(.+?)</answer>', ans, re.DOTALL)
                    if match:
                        extracted_answers.append(match.group(1).strip())
                    else:
                        extracted_answers.append(ans)
                answer = extracted_answers
            
            # completionsから応答を抽出
            responses = []
            for completion in completions:
                if isinstance(completion, str):
                    responses.append(completion)
                elif isinstance(completion, list) and len(completion) > 0:
                    responses.append(completion[0].get("content", "") if isinstance(completion[0], dict) else str(completion[0]))
                else:
                    responses.append("")
        else:
            # 古いインターフェース
            responses = kwargs.get('completions', [])
            if not responses and 'responses' in kwargs:
                responses = kwargs['responses']
        
        # 答えがリストでない場合はリストに変換
        if not isinstance(answer, list):
            answer = [answer] * len(responses)
        elif len(answer) == 1 and len(responses) > 1:
            answer = answer * len(responses)
        
        extracted_responses = [
            guess.group(1)
            if (guess := self.match_format.search(r)) is not None else None
            for r in responses
        ]
        
        scores = []
        
        for guess, true_answer in zip(extracted_responses, answer):
            score = 0
            
            # フォーマットエラー
            if guess is None:
                scores.append(-3.0)  # 厳しいペナルティ
                continue
            
            # 答えをクリーンアップ
            guess = guess.strip()
            true_answer = str(true_answer).strip()
            
            # 助数詞の評価
            score = self._evaluate_counter_answer(guess, true_answer)
            
            scores.append(score)
        
        # 抽出された回答をkwargsに追加（ログ記録用）
        kwargs['extracted_responses'] = extracted_responses
        
        return scores
    
    def _evaluate_counter_answer(self, guess: str, answer: str) -> float:
        """助数詞の答えを詳細評価"""
        # 完全一致
        if guess == answer:
            return 2.0
        
        # 数字と助数詞を分離
        guess_num, guess_counter = self._extract_number_and_counter(guess)
        answer_num, answer_counter = self._extract_number_and_counter(answer)
        
        # 数字が違う場合は大きなペナルティ
        if guess_num != answer_num:
            return -2.0
        
        # 数字は正しいが助数詞が違う場合
        if guess_num == answer_num and guess_counter != answer_counter:
            # 同じカテゴリー内の間違い
            guess_category = self.counter_to_category.get(guess_counter, None)
            answer_category = self.counter_to_category.get(answer_counter, None)
            
            if guess_category and answer_category:
                if guess_category == answer_category:
                    # 同カテゴリー内（例：つ vs 個）
                    return 0.2
                elif self._are_related_categories(guess_category, answer_category):
                    # 関連カテゴリー（例：匹 vs 羽）
                    return -0.5
                else:
                    # 無関係なカテゴリー
                    return -1.0
            else:
                # カテゴリー不明
                return -1.0
        
        # その他の場合
        return -1.5
    
    def _extract_number_and_counter(self, text: str):
        """数字と助数詞を分離"""
        # 漢数字を含む数字パターン
        num_pattern = r'([0-9０-９一二三四五六七八九十百千万]+)'
        match = re.match(num_pattern + r'(.+)', text)
        if match:
            return match.group(1), match.group(2)
        return None, text
    
    def _are_related_categories(self, cat1: str, cat2: str) -> bool:
        """カテゴリーが関連しているかチェック"""
        related_groups = [
            {"animals_small", "animals_large", "birds"},  # 動物系
            {"flat_objects", "letters"},  # 平たいもの系
            {"small_objects", "vehicles"},  # 物体系
            {"times", "order"},  # 回数・順序系
        ]
        
        for group in related_groups:
            if cat1 in group and cat2 in group:
                return True
        return False
    
    def enhanced_counter_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """強化された助数詞品質評価（説明の質を重視）"""
        if prompts is not None and completions is not None:
            responses = completions
            questions = []
            for prompt in prompts:
                if isinstance(prompt, list) and len(prompt) > 0:
                    question = prompt[-1].get("content", "") if isinstance(prompt[-1], dict) else str(prompt[-1])
                else:
                    question = str(prompt)
                questions.append(question)
        else:
            responses = kwargs.get('completions', [])
            questions = [kwargs.get('question', '')]
        
        scores = []
        
        for i, response in enumerate(responses):
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # reasoning部分を抽出
            reasoning_match = re.search(
                rf"{self.reasoning_start}(.*?){self.reasoning_end}", 
                text, re.DOTALL
            )
            
            if reasoning_match:
                reasoning = reasoning_match.group(1)
                
                # 助数詞説明の質を評価
                score += self._evaluate_counter_explanation(reasoning)
                
                # 答えとの整合性チェック
                extracted_match = self.match_format.search(text)
                if extracted_match and i < len(answer):
                    extracted_answer = extracted_match.group(1).strip()
                    true_answer = answer[i] if isinstance(answer, list) else answer
                    
                    # フルソリューションから答えを抽出
                    if isinstance(true_answer, str) and '<answer>' in true_answer:
                        answer_match = re.search(r'<answer>(.+?)</answer>', true_answer, re.DOTALL)
                        if answer_match:
                            true_answer = answer_match.group(1).strip()
                    
                    # 説明と答えの整合性
                    score += self._evaluate_explanation_consistency(reasoning, extracted_answer, true_answer)
            else:
                score = -1.0  # reasoning部分がない場合の強いペナルティ
            
            scores.append(score)
        
        return scores
    
    def _evaluate_counter_explanation(self, reasoning: str) -> float:
        """助数詞説明の質を評価"""
        score = 0
        
        # 助数詞に関するキーワード
        counter_keywords = [
            "助数詞", "数える", "カウンター", "単位",
            "匹", "羽", "頭", "人", "個", "つ", "枚", "冊", "本", "台",
            "動物", "鳥", "人間", "物", "平たい", "長い", "機械"
        ]
        
        # 説明の要素
        explanation_elements = [
            "ので", "ため", "から", "ます", "です",
            "使います", "数えます", "適切", "正しい"
        ]
        
        # キーワードの使用カウント
        keyword_count = sum(1 for keyword in counter_keywords if keyword in reasoning)
        element_count = sum(1 for element in explanation_elements if element in reasoning)
        
        # キーワードの使用に応じて加点
        if keyword_count >= 3:
            score += 0.4
        elif keyword_count >= 2:
            score += 0.2
        elif keyword_count >= 1:
            score += 0.1
        
        # 説明要素の使用
        if element_count >= 2:
            score += 0.2
        elif element_count >= 1:
            score += 0.1
        
        # 説明の長さと質
        length = len(reasoning)
        if 30 < length < 150:
            score += 0.2
        elif 150 <= length < 250:
            score += 0.1
        elif length >= 250:
            score -= 0.1  # 冗長すぎる
        elif length <= 30:
            score -= 0.2  # 短すぎる
        
        return min(score, 1.0)  # 最大1.0
    
    def _evaluate_explanation_consistency(self, reasoning: str, extracted: str, expected: str) -> float:
        """説明と答えの整合性を評価"""
        score = 0
        
        # 答えが正しい場合
        if extracted == expected:
            # 正しい助数詞が説明されているか
            _, counter = self._extract_number_and_counter(expected)
            if counter and counter in reasoning:
                score += 0.2
            
            # カテゴリーの説明があるか
            category = self.counter_to_category.get(counter, None)
            if category:
                category_keywords = {
                    "animals_small": ["小動物", "小さい動物"],
                    "animals_large": ["大型動物", "大きい動物"],
                    "birds": ["鳥", "鳥類"],
                    "people": ["人", "人間", "人物"],
                    "flat_objects": ["平たい", "薄い", "平面"],
                    "vehicles": ["乗り物", "機械", "車"],
                }
                
                if category in category_keywords:
                    if any(keyword in reasoning for keyword in category_keywords[category]):
                        score += 0.1
        else:
            # 答えが間違っている場合
            if extracted in reasoning:
                score -= 0.2  # 間違った答えを説明で正当化している
        
        return score
    
    def strict_format_check(self, prompts=None, completions=None, completion_ids=None, **kwargs):
        """厳格なフォーマットチェック（ペナルティ強化版）"""
        if prompts is not None and completions is not None:
            responses = completions
        else:
            responses = kwargs.get('completions', [])
        
        scores = []
        
        for response in responses:
            score = 0
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            # 完全なフォーマットチェック
            has_reasoning_start = self.reasoning_start in text
            has_reasoning_end = self.reasoning_end in text
            has_solution_start = self.solution_start in text
            has_solution_end = self.solution_end in text
            
            # すべての要素が正しい順序で存在するか
            if has_reasoning_start and has_reasoning_end and has_solution_start and has_solution_end:
                # 順序の確認
                idx_rs = text.find(self.reasoning_start)
                idx_re = text.find(self.reasoning_end)
                idx_ss = text.find(self.solution_start)
                idx_se = text.find(self.solution_end)
                
                if idx_rs < idx_re < idx_ss < idx_se:
                    score = 0.5  # 正しいフォーマット
                else:
                    score = -1.0  # 順序が間違っている
            else:
                # 欠けている要素ごとにペナルティ
                missing_count = sum([
                    not has_reasoning_start,
                    not has_reasoning_end,
                    not has_solution_start,
                    not has_solution_end
                ])
                score = -0.5 * missing_count
            
            scores.append(score)
        
        return scores
    
    def check_number_accuracy(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """数字の正確性を評価（助数詞タスク特有）"""
        if prompts is not None and completions is not None:
            responses = completions
        else:
            responses = kwargs.get('completions', [])
        
        scores = []
        
        # 答えの処理
        if answer and isinstance(answer, list):
            if len(answer) > 0 and isinstance(answer[0], str) and '<answer>' in answer[0]:
                extracted_answers = []
                for ans in answer:
                    match = re.search(r'<answer>(.+?)</answer>', ans, re.DOTALL)
                    if match:
                        extracted_answers.append(match.group(1).strip())
                    else:
                        extracted_answers.append(ans)
                answer = extracted_answers
        
        if not isinstance(answer, list):
            answer = [answer] * len(responses)
        
        for i, response in enumerate(responses):
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # 答えを抽出
            extracted_match = self.match_format.search(text)
            if extracted_match and i < len(answer):
                extracted_answer = extracted_match.group(1).strip()
                true_answer = answer[i]
                
                # 数字の一致を確認
                guess_num, _ = self._extract_number_and_counter(extracted_answer)
                answer_num, _ = self._extract_number_and_counter(true_answer)
                
                if guess_num and answer_num:
                    # 数字を正規化して比較
                    if self._normalize_number(guess_num) == self._normalize_number(answer_num):
                        score += 0.3
                    else:
                        score -= 0.5  # 数字が違う
            
            scores.append(score)
        
        return scores
    
    def _normalize_number(self, num_str: str) -> str:
        """数字を正規化（全角→半角、漢数字→アラビア数字）"""
        # 全角数字を半角に
        num_str = num_str.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        
        # 簡単な漢数字変換（1-10のみ）
        kanji_to_num = {
            '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
            '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
        }
        
        for kanji, num in kanji_to_num.items():
            num_str = num_str.replace(kanji, num)
        
        return num_str
    
    def get_balanced_reward_functions(self):
        """バランスの取れた報酬関数セットを返す"""
        return [
            self.strict_format_check,       # フォーマットチェック（厳格版）
            self.balanced_check_counter,    # 助数詞チェック（バランス版）
            self.enhanced_counter_quality,  # 品質チェック（強化版）
            self.check_number_accuracy,     # 数字正確性チェック
        ]