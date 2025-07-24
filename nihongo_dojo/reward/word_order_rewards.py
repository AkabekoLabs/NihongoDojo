"""
語順並び替えタスク専用の改良版報酬関数
"""

import re
from typing import List, Dict, Any, Optional
import difflib


class WordOrderRewardFunctions:
    """語順並び替えタスク用の改良された報酬関数"""
    
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
        
        # 日本語文法パターン
        self.SENTENCE_PATTERNS = {
            "basic": ["主語", "目的語", "動詞"],
            "time": ["時間", "主語", "場所", "動詞"],
            "complex": ["条件節", "主語", "副詞", "目的語", "動詞"]
        }
        
        # 文末パターン
        self.VERB_ENDINGS = [
            "ます", "ました", "ません", "ませんでした",
            "です", "でした", "ではありません", "ではありませんでした",
            "る", "た", "ない", "なかった",
            "だ", "だった", "ではない", "ではなかった"
        ]
    
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
    
    def balanced_check_word_order(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """バランスの取れた語順確認（より詳細な評価）"""
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
        
        # responsesから文字列を抽出
        response_texts = []
        for r in responses:
            if isinstance(r, str):
                response_texts.append(r)
            elif isinstance(r, list) and len(r) > 0:
                # リストの場合、最初の要素を取得
                if isinstance(r[0], dict) and "content" in r[0]:
                    response_texts.append(r[0]["content"])
                else:
                    response_texts.append(str(r[0]))
            else:
                response_texts.append("")
        
        extracted_responses = [
            guess.group(1)
            if (guess := self.match_format.search(text)) is not None else None
            for text in response_texts
        ]
        
        scores = []
        
        for guess, true_answer in zip(extracted_responses, answer):
            score = 0
            
            # フォーマットエラー
            if guess is None:
                scores.append(-3.0)  # より厳しいペナルティ
                continue
            
            # 答えをクリーンアップ
            guess = guess.strip()
            true_answer = str(true_answer).strip()
            
            # 語順の評価
            score = self._evaluate_word_order(guess, true_answer)
            
            scores.append(score)
        
        # 抽出された回答をkwargsに追加（ログ記録用）
        kwargs['extracted_responses'] = extracted_responses
        
        return scores
    
    def _evaluate_word_order(self, guess: str, answer: str) -> float:
        """語順の詳細評価（より繊細な部分点）"""
        # 完全一致
        if guess == answer:
            return 2.0  # 基本点を下げる
        
        # 文字列の類似度
        similarity = difflib.SequenceMatcher(None, guess, answer).ratio()
        
        # 単語レベルの評価
        guess_words = guess.split()
        answer_words = answer.split()
        
        # 単語数が同じ場合
        if len(guess_words) == len(answer_words):
            # 単語の順序評価
            correct_positions = sum(1 for i, (g, a) in enumerate(zip(guess_words, answer_words)) if g == a)
            position_score = correct_positions / len(answer_words)
            
            # 単語の包含評価（順序は違うが単語は正しい）
            common_words = set(guess_words) & set(answer_words)
            inclusion_score = len(common_words) / len(answer_words)
            
            # 文末が正しいかチェック
            verb_ending_bonus = 0
            if guess_words and answer_words:
                if guess_words[-1] == answer_words[-1]:
                    verb_ending_bonus = 0.3  # 文末が正しい
                elif any(guess.endswith(ending) and answer.endswith(ending) for ending in self.VERB_ENDINGS):
                    verb_ending_bonus = 0.2  # 同じ活用形
            
            # スコア計算
            if position_score == 1.0:
                return 2.0  # 完全一致（スペースの違いなど）
            elif position_score >= 0.8:
                return 1.5 + verb_ending_bonus
            elif position_score >= 0.6:
                return 1.0 + verb_ending_bonus
            elif inclusion_score >= 0.8:
                return 0.5 + verb_ending_bonus
            else:
                return -0.5
        
        # 単語数が異なる場合
        else:
            # 共通単語の割合
            common_words = set(guess_words) & set(answer_words)
            if len(common_words) >= len(answer_words) * 0.8:
                return 0.3
            elif similarity >= 0.7:
                return 0.1
            else:
                return -1.0
    
    def enhanced_word_order_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """強化された語順品質評価（文法説明の質を重視）"""
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
                
                # 文法説明の質を詳細評価
                score += self._evaluate_grammar_explanation(reasoning)
                
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
                    if i < len(questions):
                        score += self._evaluate_explanation_consistency(reasoning, extracted_answer, true_answer, questions[i])
            else:
                score = -1.0  # reasoning部分がない場合の強いペナルティ
            
            scores.append(score)
        
        return scores
    
    def _evaluate_grammar_explanation(self, reasoning: str) -> float:
        """文法説明の質を評価"""
        score = 0
        
        # 語順に関する用語
        word_order_terms = [
            "語順", "順番", "並び替え", "正しい順序", "文の構造",
            "主語", "述語", "目的語", "修飾語", "助詞"
        ]
        
        # 文法パターンの説明
        pattern_terms = [
            "〜てから", "〜ために", "〜けど", "〜ので", "〜について",
            "時間", "場所", "方向", "理由", "目的"
        ]
        
        # 用語の使用カウント
        order_count = sum(1 for term in word_order_terms if term in reasoning)
        pattern_count = sum(1 for term in pattern_terms if term in reasoning)
        
        # 語順用語の使用に応じて加点
        if order_count >= 3:
            score += 0.4
        elif order_count >= 2:
            score += 0.2
        elif order_count >= 1:
            score += 0.1
        
        # パターン説明があるか
        if pattern_count >= 2:
            score += 0.3
        elif pattern_count >= 1:
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
        
        # 具体的な説明があるか
        if "「" in reasoning and "」" in reasoning:  # 引用符で具体例
            score += 0.1
        
        return min(score, 1.0)  # 最大1.0
    
    def _evaluate_explanation_consistency(self, reasoning: str, extracted: str, expected: str, question: str) -> float:
        """説明と答えの整合性を評価"""
        score = 0
        
        # 答えが正しい場合
        if extracted == expected:
            # 正しい語順パターンが説明されているか
            if "正しい語順" in reasoning or "正しい順番" in reasoning:
                score += 0.3
            
            # 文法的な説明があるか
            if any(term in reasoning for term in ["主語", "述語", "目的語", "動詞"]):
                score += 0.2
        else:
            # 答えが間違っている場合
            if extracted in reasoning:
                score -= 0.2  # 間違った答えを説明で正当化している
            
            # 部分的に正しい説明があるか
            extracted_words = set(extracted.split())
            expected_words = set(expected.split())
            if len(extracted_words & expected_words) >= len(expected_words) * 0.7:
                score += 0.1  # 単語は概ね正しい
        
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
    
    def check_particle_preservation(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """助詞の保持を評価（語順タスク特有）"""
        if prompts is not None and completions is not None:
            responses = completions
        else:
            responses = kwargs.get('completions', [])
        
        # 答えの抽出
        if answer and isinstance(answer, list):
            expected_answers = []
            for ans in answer:
                if isinstance(ans, str) and '<answer>' in ans:
                    match = re.search(r'<answer>(.+?)</answer>', ans, re.DOTALL)
                    if match:
                        expected_answers.append(match.group(1).strip())
                    else:
                        expected_answers.append(ans)
                else:
                    expected_answers.append(str(ans))
        else:
            expected_answers = [str(answer)] * len(responses)
        
        # responsesから文字列を抽出
        response_texts = []
        for r in responses:
            if isinstance(r, str):
                response_texts.append(r)
            elif isinstance(r, list) and len(r) > 0:
                # リストの場合、最初の要素を取得
                if isinstance(r[0], dict) and "content" in r[0]:
                    response_texts.append(r[0]["content"])
                else:
                    response_texts.append(str(r[0]))
            else:
                response_texts.append("")
        
        extracted_responses = [
            guess.group(1)
            if (guess := self.match_format.search(text)) is not None else None
            for text in response_texts
        ]
        
        scores = []
        particles = ['は', 'が', 'を', 'に', 'で', 'と', 'から', 'まで', 'より', 'も', 'へ', 'の']
        
        for guess, expected in zip(extracted_responses, expected_answers):
            if guess is None:
                scores.append(-0.5)
                continue
            
            score = 0
            
            # 助詞の保持を確認
            expected_particles = [p for p in particles if p in expected]
            guess_particles = [p for p in particles if p in guess]
            
            # 助詞が正しく保持されているか
            if set(expected_particles) == set(guess_particles):
                score += 0.3
            elif len(set(expected_particles) & set(guess_particles)) >= len(expected_particles) * 0.8:
                score += 0.1
            else:
                score -= 0.2
            
            # 助詞の位置関係が適切か（単語との結合）
            for particle in expected_particles:
                if particle in guess:
                    # 助詞の前の単語を確認
                    exp_idx = expected.find(particle)
                    guess_idx = guess.find(particle)
                    
                    if exp_idx > 0 and guess_idx > 0:
                        exp_before = expected[max(0, exp_idx-5):exp_idx]
                        guess_before = guess[max(0, guess_idx-5):guess_idx]
                        
                        # 同じ単語に付いているか
                        if exp_before[-2:] == guess_before[-2:]:
                            score += 0.1
            
            scores.append(score)
        
        return scores
    
    def get_balanced_reward_functions(self):
        """バランスの取れた報酬関数セットを返す"""
        return [
            self.strict_format_check,           # フォーマットチェック（厳格版）
            self.balanced_check_word_order,     # 語順チェック（バランス版）
            self.enhanced_word_order_quality,   # 品質チェック（強化版）
            self.check_particle_preservation,   # 助詞保持チェック
        ]