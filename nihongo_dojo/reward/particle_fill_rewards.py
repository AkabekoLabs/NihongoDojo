"""
助詞穴埋めタスク専用の改良版報酬関数
"""

import re
from typing import List, Dict, Any, Optional


class ParticleFillRewardFunctions:
    """助詞穴埋めタスク用の改良された報酬関数"""
    
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
        
        # 一般的な助詞のリスト（頻度順）
        self.COMMON_PARTICLES = [
            "が", "を", "に", "で", "へ", "と", "の", "は", "も", "から", "まで", "より",
            "や", "など", "ので", "のに", "ても", "でも", "ては", "には", "では", "へは"
        ]
        
        # 文法的な用法カテゴリー
        self.PARTICLE_USAGE = {
            "が": ["主語", "対象"],
            "を": ["目的語", "対象", "動作の対象"],
            "に": ["場所", "方向", "時間", "相手", "基準", "立場"],
            "で": ["場所", "手段", "理由", "道具"],
            "へ": ["方向", "目的地"],
            "と": ["相手", "並列", "引用"],
            "の": ["所有", "関係", "説明"],
            "は": ["主題", "対比"],
            "も": ["並列", "追加"],
            "から": ["起点", "理由", "材料"],
            "まで": ["終点", "範囲"],
            "より": ["比較", "起点"]
        }
    
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
    
    def balanced_check_answer(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """バランスの取れた答え確認（より繊細な評価）"""
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
                scores.append(-3.0)  # より厳しいペナルティ
                continue
            
            # 答えをクリーンアップ
            guess = guess.strip()
            true_answer = str(true_answer).strip()
            
            # 助詞リストの場合の処理
            if true_answer.startswith('[') and true_answer.endswith(']'):
                # リスト形式の答えを評価
                score = self._evaluate_particle_list(guess, true_answer)
            else:
                # 単一助詞の評価
                score = self._evaluate_single_particle(guess, true_answer)
            
            scores.append(score)
        
        # 抽出された回答をkwargsに追加（ログ記録用）
        kwargs['extracted_responses'] = extracted_responses
        
        return scores
    
    def _evaluate_single_particle(self, guess: str, answer: str) -> float:
        """単一助詞の評価（より繊細な部分点）"""
        # 完全一致
        if guess == answer:
            return 2.0  # 基本点を下げる
        
        # 類似助詞の評価
        similar_particles = {
            "が": ["は"],  # 主題と主語の混同
            "は": ["が"],
            "に": ["へ", "で"],  # 方向・場所の混同
            "へ": ["に"],
            "で": ["に"],
            "を": [],  # 目的語は独特
            "から": ["より"],  # 起点の混同
            "より": ["から"]
        }
        
        # 文法的に近い助詞なら部分点
        if answer in similar_particles and guess in similar_particles[answer]:
            return 0.5
        
        # 助詞として妥当だが不正解
        if guess in self.COMMON_PARTICLES:
            return -0.5
        
        # 助詞ではない
        return -2.0
    
    def _evaluate_particle_list(self, guess: str, answer: str) -> float:
        """リスト形式の助詞答えの評価"""
        try:
            # 文字列からリストを抽出
            import ast
            true_list = ast.literal_eval(answer)
            
            # guessもリスト形式かチェック
            if guess.startswith('[') and guess.endswith(']'):
                try:
                    guess_list = ast.literal_eval(guess)
                except:
                    guess_list = [guess]
            else:
                # カンマ区切りで分割を試みる
                guess_list = [g.strip() for g in guess.split(',')]
            
            # 完全一致
            if guess_list == true_list:
                return 2.0
            
            # 部分一致の評価
            correct_count = sum(1 for g, t in zip(guess_list, true_list) if g == t)
            total = max(len(guess_list), len(true_list))
            
            if correct_count == total:
                return 2.0
            elif correct_count > 0:
                return 1.0 * (correct_count / total)
            else:
                return -1.0
                
        except:
            # リスト解析に失敗
            return -2.0
    
    def enhanced_particle_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """強化された助詞品質評価（文法説明の質を重視）"""
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
                    score += self._evaluate_explanation_consistency(reasoning, extracted_answer, true_answer)
            else:
                score = -1.0  # reasoning部分がない場合の強いペナルティ
            
            scores.append(score)
        
        return scores
    
    def _evaluate_grammar_explanation(self, reasoning: str) -> float:
        """文法説明の質を評価"""
        score = 0
        
        # 文法用語の使用（より詳細なリスト）
        basic_terms = ["助詞", "主語", "目的語", "対象", "場所", "方向"]
        advanced_terms = ["主題", "対比", "並列", "手段", "起点", "終点", "理由", "条件", "逆接"]
        
        basic_count = sum(1 for term in basic_terms if term in reasoning)
        advanced_count = sum(1 for term in advanced_terms if term in reasoning)
        
        # 文法用語の使用に応じて加点
        if basic_count >= 2:
            score += 0.3
        elif basic_count >= 1:
            score += 0.1
        
        if advanced_count >= 1:
            score += 0.2
        
        # 具体的な助詞の言及
        particle_mentions = sum(1 for p in self.COMMON_PARTICLES if f"「{p}」" in reasoning or f"'{p}'" in reasoning)
        if particle_mentions >= 2:
            score += 0.2
        elif particle_mentions >= 1:
            score += 0.1
        
        # 説明の長さと質
        length = len(reasoning)
        if 30 < length < 100:
            score += 0.2
        elif 100 <= length < 200:
            score += 0.1
        elif length >= 200:
            score -= 0.1  # 冗長すぎる説明はペナルティ
        elif length <= 30:
            score -= 0.2  # 短すぎる説明もペナルティ
        
        # 具体的な用法の説明があるか
        usage_keywords = ["表す", "使います", "示す", "表現", "意味"]
        if any(keyword in reasoning for keyword in usage_keywords):
            score += 0.1
        
        return min(score, 1.0)  # 最大1.0
    
    def _evaluate_explanation_consistency(self, reasoning: str, extracted: str, expected: str) -> float:
        """説明と答えの整合性を評価"""
        score = 0
        
        # 答えが正しい場合
        if extracted == expected:
            # 正しい助詞の用法が説明されているか
            if expected in self.PARTICLE_USAGE:
                usages = self.PARTICLE_USAGE[expected]
                if any(usage in reasoning for usage in usages):
                    score += 0.5
                else:
                    score += 0.2  # 正解だが説明が不適切
            else:
                score += 0.3
        else:
            # 答えが間違っている場合、説明も評価
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
    
    def get_balanced_reward_functions(self):
        """バランスの取れた報酬関数セットを返す"""
        return [
            self.strict_format_check,           # フォーマットチェック（厳格版）
            self.balanced_check_answer,         # 答えチェック（バランス版）
            self.enhanced_particle_quality,     # 品質チェック（強化版）
        ]