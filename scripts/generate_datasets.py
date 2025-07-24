#!/usr/bin/env python
"""
Nihongo DoJo データセット生成スクリプト
事前生成された大規模データセットを作成
"""

import argparse
import os
import sys
import json
from pathlib import Path
from typing import List, Optional

from nihongo_dojo.data.dataset_builder import create_all_preset_datasets
from nihongo_dojo.data.large_scale_datasets import (
    LargeScaleDatasetGenerator,
    DatasetSerializer,
    generate_preset_dataset
)
from nihongo_dojo.core import TaskDifficulty, TaskType


def main():
    parser = argparse.ArgumentParser(
        description="Nihongo DoJo大規模データセット生成ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  # 学年1,2,3の漢字読みタスクを生成
  python generate_datasets.py --grades 1 2 3 --tasks KANJI_READING
  
  # 全タスクタイプで中級レベルのデータセットを生成
  python generate_datasets.py --preset medium
  
  # カスタムサイズで特定のタスクを生成
  python generate_datasets.py --custom-size 10000 --tasks KANJI_READING KANJI_WRITING
        """
    )
    
    # 基本設定
    parser.add_argument(
        "--preset",
        type=str,
        choices=["small", "medium", "large", "extra_large", "all"],
        help="生成するデータセットのプリセット（grades/tasksと併用不可）"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./datasets",
        help="出力ディレクトリ"
    )
    
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["json", "jsonl", "parquet", "csv"],
        default="jsonl",
        help="出力フォーマット"
    )
    
    # グレードとタスク指定
    parser.add_argument(
        "--grades",
        type=int,
        nargs="+",
        choices=[1, 2, 3, 4, 5, 6],
        help="対象学年（1-6）"
    )
    
    parser.add_argument(
        "--tasks",
        type=str,
        nargs="+",
        help="生成するタスクタイプ（例: KANJI_READING KANJI_WRITING）"
    )
    
    # カスタマイズオプション
    parser.add_argument(
        "--custom-size",
        type=int,
        help="カスタムサイズのデータセット（タスク数）"
    )
    
    parser.add_argument(
        "--task-distribution",
        type=str,
        help="タスクタイプの分布（例: basic:0.6,advanced:0.3,cultural:0.1）"
    )
    
    parser.add_argument(
        "--difficulty-distribution",
        type=str,
        default="beginner:0.25,intermediate:0.35,advanced:0.25,native:0.15",
        help="難易度の分布"
    )
    
    parser.add_argument(
        "--num-workers",
        type=int,
        help="並列処理のワーカー数"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="ランダムシード"
    )
    
    parser.add_argument(
        "--compress",
        action="store_true",
        help="出力ファイルを圧縮する"
    )
    
    args = parser.parse_args()
    
    # 引数の妥当性チェック
    if args.preset and (args.grades or args.tasks):
        parser.error("--presetと--grades/--tasksは同時に指定できません")
    
    if not args.preset and not args.grades and not args.tasks and not args.custom_size:
        parser.error("--preset、--grades/--tasks、または--custom-sizeのいずれかを指定してください")
    
    # 出力ディレクトリ作成
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # タスクタイプのフィルタリング準備
    selected_tasks = None
    if args.tasks:
        selected_tasks = []
        for task_name in args.tasks:
            try:
                task_type = TaskType[task_name]
                selected_tasks.append(task_type)
            except KeyError:
                print(f"警告: 不明なタスクタイプ '{task_name}' はスキップされます")
                print(f"利用可能なタスクタイプ: {', '.join([t.name for t in TaskType])}")
        
        if not selected_tasks:
            parser.error("有効なタスクタイプが指定されていません")
    
    # グレードとタスクが指定された場合
    if args.grades or args.tasks:
        try:
            from nihongo_dojo.data.huggingface_dataset_builder import HuggingFaceDatasetBuilder
        except ImportError:
            from data.huggingface_dataset_builder import HuggingFaceDatasetBuilder
        
        builder = HuggingFaceDatasetBuilder()
        
        # 出力ファイル名の生成
        output_name = "nihongo-dojo"
        if args.grades:
            output_name += f"-grades{'-'.join(map(str, args.grades))}"
        if args.tasks:
            task_names = '-'.join([t.name.lower() for t in selected_tasks])
            output_name += f"-{task_names}"
        
        output_path = os.path.join(args.output_dir, output_name)
        
        print(f"🎯 カスタムデータセット生成:")
        if args.grades:
            print(f"   学年: {', '.join(map(str, args.grades))}")
        if selected_tasks:
            print(f"   タスク: {', '.join([t.value for t in selected_tasks])}")
        
        # データセット生成
        if selected_tasks and len(selected_tasks) == 1 and selected_tasks[0] == TaskType.PARTICLE_FILL:
            # 助詞穴埋めタスクのみの場合
            print(f"💾 データセット保存中: {output_path}")
            dataset = builder.create_grpo_dataset(
                num_groups=args.custom_size // 4 if args.custom_size else 500,
                group_size=4,
                task_types=[TaskType.PARTICLE_FILL]
            )
        elif selected_tasks and (TaskType.KANJI_READING in selected_tasks or TaskType.KANJI_WRITING in selected_tasks):
            # 漢字読み/書きタスクの場合
            dataset = builder.create_kanji_reading_dataset(
                num_samples_per_grade=1000,
                grades=args.grades or [1, 2, 3, 4, 5, 6],
                include_on_yomi=True,
                include_kun_yomi=True,
                include_writing=(TaskType.KANJI_WRITING in selected_tasks)
            )
        else:
            # その他のタスクまたは混合タスクの場合
            dataset = builder.create_grpo_dataset(
                num_groups=args.custom_size // 4 if args.custom_size else 1000,
                group_size=4,
                task_types=selected_tasks
            )
        
        # データセット保存
        if args.output_format == "json":
            # JSON形式で保存
            all_data = []
            
            # DatasetDictの場合とDatasetの場合を処理
            from datasets import DatasetDict
            if isinstance(dataset, DatasetDict):
                # DatasetDictの場合
                for split in ['train', 'validation', 'test']:
                    if split in dataset:
                        all_data.extend(dataset[split])
            else:
                # 単一のDatasetの場合
                all_data = list(dataset)
            
            output_file = f"{output_path}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ データセット生成完了: {output_file}")
            print(f"   総サンプル数: {len(all_data):,}")
        
        elif args.output_format == "jsonl":
            # JSONL形式で保存
            output_file = f"{output_path}.jsonl"
            if args.compress:
                output_file += ".gz"
            
            # DatasetDictの場合とDatasetの場合を処理
            from datasets import DatasetDict
            if isinstance(dataset, DatasetDict):
                # DatasetDictの場合
                data_dict = {'train': dataset['train'], 'validation': dataset['validation'], 'test': dataset['test']}
                num_samples = sum(len(dataset[split]) for split in ['train', 'validation', 'test'] if split in dataset)
            else:
                # 単一のDatasetの場合
                data_dict = {'all': dataset}
                num_samples = len(dataset)
            
            DatasetSerializer.save_dataset(
                data=data_dict,
                metadata={'num_samples': num_samples},
                output_dir=output_path,
                format="jsonl",
                compress=args.compress
            )
            
            print(f"✅ データセット生成完了: {output_file}")
        
        elif args.output_format == "parquet":
            # Parquet形式で保存
            dataset.save_to_disk(output_path)
            print(f"✅ データセット生成完了: {output_path}")
        
        elif args.output_format == "csv":
            # CSV形式で保存
            from datasets import DatasetDict
            if isinstance(dataset, DatasetDict):
                # DatasetDictの場合
                for split in ['train', 'validation', 'test']:
                    if split in dataset:
                        dataset[split].to_csv(f"{output_path}_{split}.csv")
            else:
                # 単一のDatasetの場合
                dataset.to_csv(f"{output_path}.csv")
            print(f"✅ データセット生成完了: {output_path}_*.csv")
    
    # タスク分布の処理
    elif args.task_distribution:
        task_dist = {}
        for item in args.task_distribution.split(","):
            key, value = item.split(":")
            task_dist[key] = float(value)
    
        # 難易度分布のパース
        diff_dist = {}
        diff_mapping = {
            "beginner": TaskDifficulty.BEGINNER,
            "intermediate": TaskDifficulty.INTERMEDIATE,
            "advanced": TaskDifficulty.ADVANCED,
            "native": TaskDifficulty.NATIVE
        }
        for item in args.difficulty_distribution.split(","):
            key, value = item.split(":")
            diff_dist[diff_mapping[key]] = float(value)
        
        if args.preset == "all":
            # 全プリセット生成
            print("🎯 全プリセットデータセットを生成します")
            create_all_preset_datasets(args.output_dir)
        
        elif args.custom_size:
            # カスタムサイズ
            print(f"🎯 カスタムデータセット生成: {args.custom_size:,}タスク")
            
            generator = LargeScaleDatasetGenerator(num_workers=args.num_workers)
            
            output_name = f"nihongo-dojo-custom-{args.custom_size}"
            output_path = os.path.join(args.output_dir, output_name)
            
            data, metadata = generator.generate_large_dataset(
                total_tasks=args.custom_size,
                task_type_distribution=task_dist,
                difficulty_distribution=diff_dist,
                seed=args.seed
            )
            
            DatasetSerializer.save_dataset(
                data=data,
                metadata=metadata,
                output_dir=output_path,
                format=args.output_format,
                compress=args.compress
            )
            
            print(f"✅ カスタムデータセット生成完了: {output_path}")
        
        else:
            # プリセット生成
            print(f"🎯 プリセットデータセット生成: {args.preset}")
            
            output_path, metadata = generate_preset_dataset(
                preset=args.preset,
                output_dir=os.path.join(args.output_dir, f"nihongo-dojo-{args.preset}"),
                task_type_distribution=task_dist,
                difficulty_distribution=diff_dist,
                seed=args.seed
            )
            
            print(f"✅ データセット生成完了: {output_path}")
            print(f"   タスク数: {metadata.num_tasks:,}")
            print(f"   グループ数: {metadata.num_groups:,}")
    
    else:
        # デフォルトのプリセット処理
        preset = args.preset or "medium"
        print(f"🎯 プリセットデータセット生成: {preset}")
        
        # デフォルトのタスク分布
        default_task_dist = {"basic": 0.6, "advanced": 0.3, "cultural": 0.1}
        
        # デフォルトの難易度分布
        default_diff_dist = {
            TaskDifficulty.BEGINNER: 0.25,
            TaskDifficulty.INTERMEDIATE: 0.35,
            TaskDifficulty.ADVANCED: 0.25,
            TaskDifficulty.NATIVE: 0.15
        }
        
        output_path, metadata = generate_preset_dataset(
            preset=preset,
            output_dir=os.path.join(args.output_dir, f"nihongo-dojo-{preset}"),
            task_type_distribution=default_task_dist,
            difficulty_distribution=default_diff_dist,
            seed=args.seed
        )
        
        print(f"✅ データセット生成完了: {output_path}")
        print(f"   タスク数: {metadata.num_tasks:,}")
        print(f"   グループ数: {metadata.num_groups:,}")


if __name__ == "__main__":
    main()