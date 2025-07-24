"""
Colab環境用のログ管理機能
"""

import os
import json
from datetime import datetime
import numpy as np


class TrainingLogger:
    """学習ログを管理するクラス"""
    
    def __init__(self, log_dir="./logs", task_name="training", enable_detailed_logging=True):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 日付ベースのログファイル名（タスク名を含む）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_filename = os.path.join(log_dir, f"{task_name}_training_{timestamp}.jsonl")
        self.history_filename = self.log_filename.replace('.jsonl', '_history.jsonl')
        self.detailed_log_filename = self.log_filename.replace('.jsonl', '_detailed.jsonl')
        
        # ログ記録用の変数
        self.training_logs = []
        self.reward_logs = []
        self.printed_times = 0
        self.enable_detailed_logging = enable_detailed_logging
        
        # 詳細統計の追跡
        self.batch_statistics = []
        self.reward_function_stats = {}
        
        print(f"ログファイル: {self.log_filename}")
        print(f"学習履歴ファイル: {self.history_filename}")
        if enable_detailed_logging:
            print(f"詳細ログファイル: {self.detailed_log_filename}")
        print("※ 学習履歴は1ステップごとに自動保存されます")
    
    def log_step(self, step, question, answer, responses, extracted_responses, rewards):
        """ステップごとのログを記録"""
        # extracted_responsesがNoneまたは空の場合、responsesから抽出を試みる
        if not extracted_responses or all(r is None for r in extracted_responses):
            extracted_responses = []
            for response in responses:
                extracted = self._extract_answer_from_completion(response)
                extracted_responses.append(extracted)
        
        log_entry = {
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'question': question,
            'answer': answer,
            'responses': responses,
            'extracted': extracted_responses,
            'rewards': rewards
        }
        
        self.reward_logs.append(log_entry)
        
        # JSONファイルに毎ステップ保存
        with open(self.log_filename, 'a', encoding='utf-8') as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write('\n')
        
        self.printed_times += 1
        return log_entry
    
    def log_detailed_batch(self, step, batch_prompts, batch_completions, batch_answers, batch_rewards, reward_function_name):
        """バッチ単位の詳細ログを記録（全ての生成結果を保存）"""
        # 入力データの正規化
        if not isinstance(batch_prompts, list):
            batch_prompts = [batch_prompts]
        if not isinstance(batch_completions, list):
            batch_completions = [batch_completions]
        if not isinstance(batch_answers, list):
            batch_answers = [batch_answers]
        if not isinstance(batch_rewards, list):
            batch_rewards = [batch_rewards]
        
        # バッチサイズの調整（最小サイズに合わせる）
        batch_size = min(len(batch_prompts), len(batch_completions), len(batch_answers), len(batch_rewards))
        
        detailed_log_entry = {
            'step': step,
            'timestamp': datetime.now().isoformat(),
            'reward_function': reward_function_name,
            'batch_size': batch_size,
            'batch_data': []
        }
        
        # 各プロンプトとその全ての生成結果を記録
        for i in range(batch_size):
            prompt = batch_prompts[i] if i < len(batch_prompts) else batch_prompts[0]
            completions = batch_completions[i] if i < len(batch_completions) else batch_completions[0]
            answer = batch_answers[i] if i < len(batch_answers) else batch_answers[0]
            rewards = batch_rewards[i] if i < len(batch_rewards) else batch_rewards[0]
            # プロンプトから質問を抽出
            if isinstance(prompt, list) and len(prompt) > 0:
                question = prompt[-1].get("content", "") if isinstance(prompt[-1], dict) else str(prompt[-1])
            else:
                question = str(prompt)
            
            # rewardsがlistでない場合の処理
            if not isinstance(rewards, list):
                rewards = [rewards]
            
            # completionsがlistでない場合の処理
            if not isinstance(completions, list):
                completions = [completions]
            
            # 各生成結果の詳細を記録
            generations = []
            for j, (completion, reward) in enumerate(zip(completions, rewards)):
                # completionがdictの場合、contentを取得
                if isinstance(completion, dict):
                    completion_text = completion.get('content', str(completion))
                else:
                    completion_text = str(completion)
                
                generation_data = {
                    'generation_id': j,
                    'completion': completion_text,
                    'reward': reward,
                    'extracted_answer': self._extract_answer_from_completion(completion_text) if completion_text else None
                }
                generations.append(generation_data)
            
            batch_item = {
                'item_id': i,
                'question': question,
                'expected_answer': answer,
                'generations': generations,
                'generation_count': len(generations)
            }
            detailed_log_entry['batch_data'].append(batch_item)
        
        # 詳細ログファイルに保存
        try:
            detailed_log_filename = self.log_filename.replace('.jsonl', '_detailed.jsonl')
            with open(detailed_log_filename, 'a', encoding='utf-8') as f:
                json.dump(detailed_log_entry, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            print(f"詳細ログファイルの保存中にエラーが発生しました: {e}")
        
        return detailed_log_entry
    
    def _extract_answer_from_completion(self, completion):
        """生成されたテキストから回答を抽出"""
        if not completion:
            return None
        
        # completionがlistの場合、最初の要素を取得
        if isinstance(completion, list):
            if len(completion) > 0:
                completion = completion[0]
            else:
                return None
        
        # completionがdictの場合、contentを取得
        if isinstance(completion, dict):
            completion = completion.get('content', str(completion))
        
        completion = str(completion)
        
        # <answer>タグから回答を抽出
        import re
        answer_pattern = r'<answer>(.*?)</answer>'
        match = re.search(answer_pattern, completion, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # タグがない場合でも、改行を除去して最初の50文字を返す
        cleaned = completion.strip().replace('\n', ' ')[:50]
        return cleaned if cleaned else None
    
    
    def log_reward_function_stats(self, function_name, stats):
        """報酬関数ごとの統計を記録"""
        if function_name not in self.reward_function_stats:
            self.reward_function_stats[function_name] = []
        self.reward_function_stats[function_name].append(stats)
    
    def get_summary_stats(self):
        """ログのサマリー統計を取得"""
        if not self.reward_logs:
            return {}
        
        rewards = [entry['rewards'][0] for entry in self.reward_logs if entry['rewards']]
        return {
            'total_steps': len(self.reward_logs),
            'average_reward': np.mean(rewards) if rewards else 0,
            'max_reward': np.max(rewards) if rewards else 0,
            'min_reward': np.min(rewards) if rewards else 0,
            'reward_function_stats': self.reward_function_stats
        }



class LoggingRewardWrapper:
    """報酬関数にログ機能を追加するラッパークラス"""
    
    def __init__(self, reward_func, logger, print_every_steps=5):
        self.reward_func = reward_func
        self.logger = logger
        self.print_every_steps = print_every_steps
        self.printed_times = 0
        # __name__属性を追加（元の関数名を保持）
        self.__name__ = f"LoggingWrapper_{reward_func.__name__}"
    
    def __call__(self, prompts=None, completions=None, completion_ids=None, 
                 question=None, answer=None, responses=None, extracted_responses=None, **kwargs):
        """報酬関数を実行し、ログを記録（GRPOTrainerの新しいインターフェースに対応）"""
        
        # 新しいインターフェース（prompts, completions）の場合
        if prompts is not None and completions is not None:
            # answerパラメータが提供されていて、それがフルソリューションの場合、
            # 実際の答えを抽出する
            actual_answers = answer
            if answer and len(answer) > 0 and isinstance(answer[0], str):
                # answer[0]がフルソリューション（<reasoning>...</reasoning><answer>...</answer>形式）の場合
                import re
                if '<answer>' in answer[0] and '</answer>' in answer[0]:
                    # フルソリューションから実際の答えを抽出
                    actual_answers = []
                    for ans in answer:
                        match = re.search(r'<answer>(.+?)</answer>', ans, re.DOTALL)
                        if match:
                            actual_answers.append(match.group(1).strip())
                        else:
                            actual_answers.append(ans)  # フォールバック
            
            # answerパラメータを追加して元の報酬関数を呼び出し
            scores = self.reward_func(prompts=prompts, completions=completions, 
                                    completion_ids=completion_ids, answer=actual_answers, **kwargs)
            
            # ログ用にデータを抽出
            if prompts and len(prompts) > 0:
                # 質問を抽出
                if isinstance(prompts[0], str):
                    question = prompts[0]
                else:
                    # メッセージ形式の場合、最後のユーザーメッセージを取得
                    question = prompts[0][-1].get("content", "") if isinstance(prompts[0], list) else ""
                
                # 回答を抽出（報酬関数が設定した値を優先、なければ直接抽出）
                extracted_responses = kwargs.get('extracted_responses', [])
                if not extracted_responses or all(r is None for r in extracted_responses):
                    extracted_responses = []
                    for completion in completions:
                        extracted = self.logger._extract_answer_from_completion(completion)
                        extracted_responses.append(extracted)
                
                # 各生成結果に対してログを記録
                for i, (completion, score) in enumerate(zip(completions, scores)):
                    # ログエントリを作成
                    log_entry = {
                        'step': self.printed_times,
                        'question': question,
                        'answer': actual_answers[i] if actual_answers and i < len(actual_answers) else "",
                        'full_solution': answer[i] if answer and i < len(answer) else "",
                        'completion': completion,
                        'extracted_response': extracted_responses[i] if i < len(extracted_responses) else None,
                        'score': score,
                        'reward_func': self.reward_func.__name__
                    }
                    
                    # ステップログとして記録
                    self.logger.log_step(
                        step=self.printed_times,
                        question=question,
                        answer=actual_answers[i] if actual_answers and i < len(actual_answers) else "",
                        responses=[completion],
                        extracted_responses=[extracted_responses[i]] if i < len(extracted_responses) else [None],
                        rewards=[score]
                    )
            
            # 定期的に情報を出力
            self.printed_times += 1
            if self.printed_times % self.print_every_steps == 0:
                print(f"\n[Step {self.printed_times}] 処理中...")
                if prompts and len(prompts) > 0:
                    print(f"質問: {question[:100]}...")
                if actual_answers and len(actual_answers) > 0:
                    print(f"正解: {actual_answers[0]}")
                if completions and len(completions) > 0:
                    print(f"生成例: {completions[0][:200]}...")
                if extracted_responses and len(extracted_responses) > 0:
                    print(f"抽出された回答: {extracted_responses[0] if extracted_responses[0] else '(抽出できず)'}")
                if scores:
                    print(f"スコア: {scores[0]:.2f}")
                    # 各応答のスコアも表示
                    if len(scores) > 1:
                        print(f"全スコア: {[f'{s:.2f}' for s in scores]}")
                
                # 報酬関数の統計を記録
                if hasattr(self.logger, 'log_reward_function_stats'):
                    stats = {
                        'step': self.printed_times,
                        'mean_score': np.mean(scores) if scores else 0,
                        'max_score': np.max(scores) if scores else 0,
                        'min_score': np.min(scores) if scores else 0,
                        'std_score': np.std(scores) if scores else 0
                    }
                    self.logger.log_reward_function_stats(self.reward_func.__name__, stats)
                
                # 詳細バッチログを記録
                if hasattr(self.logger, 'log_detailed_batch') and self.logger.enable_detailed_logging:
                    try:
                        # バッチデータを適切な形式に変換
                        batch_prompts = prompts if isinstance(prompts, list) else [prompts]
                        batch_completions = completions if isinstance(completions, list) else [completions]
                        batch_answers = actual_answers if isinstance(actual_answers, list) else [actual_answers]
                        batch_rewards = scores if isinstance(scores, list) else [scores]
                        
                        self.logger.log_detailed_batch(
                            step=self.printed_times,
                            batch_prompts=batch_prompts,
                            batch_completions=batch_completions,
                            batch_answers=batch_answers,
                            batch_rewards=batch_rewards,
                            reward_function_name=self.reward_func.__name__
                        )
                    except Exception as e:
                        print(f"詳細ログ記録中にエラーが発生しました: {e}")
                        # エラーが発生してもトレーニングを継続する
        
        # 古いインターフェース（question, answer）の場合（互換性のため）
        else:
            scores = self.reward_func(question, answer, responses, extracted_responses)
            
            # ログ記録
            self.logger.log_step(
                step=self.printed_times,
                question=question,
                answer=answer[0] if answer else None,
                responses=responses,
                extracted_responses=extracted_responses,
                rewards=scores
            )
            
            # 定期的に情報を出力
            self.printed_times += 1
            if self.printed_times % self.print_every_steps == 0:
                print(f"\n[Step {self.printed_times}] サンプル質問: {question[:50]}...")
                if answer and len(answer) > 0:
                    print(f"期待される答え: {answer[0]}")
                if extracted_responses and len(extracted_responses) > 0:
                    print(f"モデルの回答: {extracted_responses[0] if extracted_responses[0] else '(抽出できず)'}")
        
        return scores