"""
Script to upload Nihongo DoJo datasets to Hugging Face Hub
"""

import os
import sys
import argparse
import json
import gzip
from pathlib import Path
from typing import List, Dict, Optional
from datasets import Dataset, DatasetDict, load_dataset
from huggingface_hub import HfApi, create_repo

from nihongo_dojo.data.huggingface_dataset_builder import HuggingFaceDatasetBuilder


def generate_dataset_card(dataset_name: str, dataset: DatasetDict, source_path: str) -> str:
    """
    汎用データセットカードを生成
    """
    total_samples = sum(len(dataset[split]) for split in dataset)
    splits_info = "\n".join([f"- {split}: {len(dataset[split]):,} サンプル" for split in dataset])
    
    # サンプルデータの取得
    sample_data = ""
    if 'train' in dataset and len(dataset['train']) > 0:
        sample = dataset['train'][0]
        # sampleが辞書型でない場合は、データセットから辞書として取得
        if hasattr(sample, 'to_dict'):
            sample_dict = sample.to_dict()
        elif isinstance(sample, dict):
            sample_dict = sample
        else:
            # DatasetのRowから辞書を作成
            sample_dict = {key: sample[key] for key in dataset['train'].column_names}
        sample_data = f"""
## サンプルデータ

```json
{json.dumps(sample_dict, ensure_ascii=False, indent=2)[:1000]}...
```
"""
    
    return f"""---
language:
- ja
license: mit
task_categories:
- text-generation
- question-answering
tags:
- japanese
- education
- grpo
pretty_name: {dataset_name}
size_categories:
- {get_size_category(total_samples)}
---

# {dataset_name}

このデータセットは、Nihongo DoJoフレームワークを使用して生成された日本語学習用データセットです。

## データセット統計

{splits_info}
- 総サンプル数: {total_samples:,}

## ソース

生成元: `{source_path}`

{sample_data}

## 使用方法

```python
from datasets import load_dataset

dataset = load_dataset("{dataset_name}")
print(dataset['train'][0])
```

## ライセンス

MIT License
"""


def get_size_category(num_samples: int) -> str:
    """サンプル数からサイズカテゴリを決定"""
    if num_samples < 1000:
        return "n<1K"
    elif num_samples < 10000:
        return "1K<n<10K"
    elif num_samples < 100000:
        return "10K<n<100K"
    elif num_samples < 1000000:
        return "100K<n<1M"
    else:
        return "1M<n<10M"


def generate_kanji_dataset_card(dataset_name: str, grades: List[int], dataset: DatasetDict) -> str:
    """漢字データセット用のカードを生成（レガシー）"""
    return f"""---
language:
- ja
license: mit
task_categories:
- text-generation
- question-answering
tags:
- japanese
- kanji
- education
- grpo
pretty_name: {dataset_name}
size_categories:
- {get_size_category(sum(len(dataset[split]) for split in dataset))}
---

# {dataset_name}

小学校{min(grades)}年生から{max(grades)}年生までの教育漢字を収録した漢字読み練習用データセットです。

## 統計情報

- 訓練データ: {len(dataset.get('train', [])):,} サンプル
- 検証データ: {len(dataset.get('validation', [])):,} サンプル
- テストデータ: {len(dataset.get('test', [])):,} サンプル

## ライセンス

MIT License
"""


def load_local_dataset(path: str) -> Dict:
    """
    ローカルのデータセットファイルを読み込む
    
    Args:
        path: データセットファイルまたはディレクトリのパス
    
    Returns:
        データセットの辞書
    """
    path = Path(path)
    
    if path.is_file():
        # ファイルの場合
        if path.suffix == '.json':
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {'train': data}
        
        elif path.suffix == '.jsonl' or (path.suffix == '.gz' and path.stem.endswith('.jsonl')):
            data = []
            if path.suffix == '.gz':
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    for line in f:
                        data.append(json.loads(line))
            else:
                with open(path, 'r', encoding='utf-8') as f:
                    for line in f:
                        data.append(json.loads(line))
            return {'train': data}
        
        elif path.suffix == '.parquet':
            dataset = load_dataset('parquet', data_files=str(path))
            return dataset
        
        elif path.suffix == '.csv':
            dataset = load_dataset('csv', data_files=str(path))
            return dataset
    
    elif path.is_dir():
        # ディレクトリの場合
        dataset_dict = {}
        
        # まず data.jsonl.gz または data.jsonl を探す（generate_datasets.pyの出力形式）
        data_jsonl_gz = path / "data.jsonl.gz"
        data_jsonl = path / "data.jsonl"
        
        if data_jsonl_gz.exists():
            data = []
            with gzip.open(data_jsonl_gz, 'rt', encoding='utf-8') as f:
                for line in f:
                    data.append(json.loads(line))
            # データを分割
            total = len(data)
            train_size = int(total * 0.8)
            val_size = int(total * 0.1)
            dataset_dict['train'] = data[:train_size]
            dataset_dict['validation'] = data[train_size:train_size+val_size]
            dataset_dict['test'] = data[train_size+val_size:]
            return dataset_dict
        elif data_jsonl.exists():
            data = []
            with open(data_jsonl, 'r', encoding='utf-8') as f:
                for line in f:
                    data.append(json.loads(line))
            # データを分割
            total = len(data)
            train_size = int(total * 0.8)
            val_size = int(total * 0.1)
            dataset_dict['train'] = data[:train_size]
            dataset_dict['validation'] = data[train_size:train_size+val_size]
            dataset_dict['test'] = data[train_size+val_size:]
            return dataset_dict
        
        # 次に split別のファイルを探す
        for split in ['train', 'validation', 'test']:
            jsonl_file = path / f"{split}.jsonl"
            jsonl_gz_file = path / f"{split}.jsonl.gz"
            
            if jsonl_gz_file.exists():
                data = []
                with gzip.open(jsonl_gz_file, 'rt', encoding='utf-8') as f:
                    for line in f:
                        data.append(json.loads(line))
                dataset_dict[split] = data
            elif jsonl_file.exists():
                data = []
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data.append(json.loads(line))
                dataset_dict[split] = data
        
        if dataset_dict:
            return dataset_dict
        
        # Parquetファイルを探す
        parquet_files = list(path.glob("*.parquet"))
        if parquet_files:
            return load_dataset('parquet', data_dir=str(path))
        
        # CSVファイルを探す
        csv_files = list(path.glob("*.csv"))
        if csv_files:
            data_files = {}
            for csv_file in csv_files:
                split = csv_file.stem.split('_')[-1]
                if split in ['train', 'validation', 'test']:
                    data_files[split] = str(csv_file)
            return load_dataset('csv', data_files=data_files)
    
    raise ValueError(f"サポートされていないファイル形式またはディレクトリ構造: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Nihongo DoJo データセットをHugging Face Hubにアップロード",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  # generate_datasets.pyで生成したデータセットをアップロード
  python upload_to_huggingface.py --input-path ./datasets/nihongo-dojo-medium --dataset-name nihongo-dojo-medium
  
  # 組織アカウントにプライベートでアップロード
  python upload_to_huggingface.py --input-path ./datasets/custom.jsonl --dataset-name my-dataset --organization my-org --private
  
  # 新規にデータセットを生成してアップロード（レガシーモード）
  python upload_to_huggingface.py --dataset-name nihongo-kanji --dataset-type kanji --grades 1 2 3
        """
    )
    
    # データセット入力オプション
    parser.add_argument("--input-path", type=str, help="アップロードするローカルデータセットのパス")
    
    # Hugging Face設定
    parser.add_argument("--dataset-name", type=str, required=True, help="Hugging Face Hub上のデータセット名")
    parser.add_argument("--organization", type=str, default=None, help="組織名（オプション）")
    parser.add_argument("--private", action="store_true", help="データセットをプライベートにする")
    parser.add_argument("--token", type=str, default=None, help="HuggingFace APIトークン")
    
    # レガシーオプション（後方互換性のため）
    parser.add_argument("--dataset-type", type=str, choices=["kanji", "grpo", "chat", "all"], help="生成するデータセットタイプ（レガシー）")
    parser.add_argument("--grades", type=int, nargs="+", help="対象学年（レガシー）")
    
    args = parser.parse_args()
    
    # Hugging Face API token
    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        print("警告: HuggingFaceトークンが提供されていません。`huggingface-cli login`でログインする必要があるかもしれません")
    
    # Repository name
    repo_id = f"{args.organization}/{args.dataset_name}" if args.organization else args.dataset_name
    
    # 入力パスが指定されている場合（推奨）
    if args.input_path:
        print(f"📁 ローカルデータセットを読み込み中: {args.input_path}")
        
        try:
            # データセットを読み込む
            dataset_dict = load_local_dataset(args.input_path)
            
            # DatasetDictに変換
            if isinstance(dataset_dict, dict):
                datasets_to_upload = {}
                for split, data in dataset_dict.items():
                    if isinstance(data, list):
                        # メタデータフィールドをJSON文字列に変換
                        processed_data = []
                        for item in data:
                            processed_item = item.copy()
                            if 'metadata' in processed_item and isinstance(processed_item['metadata'], dict):
                                processed_item['metadata'] = json.dumps(processed_item['metadata'], ensure_ascii=False)
                            processed_data.append(processed_item)
                        datasets_to_upload[split] = Dataset.from_list(processed_data)
                    else:
                        datasets_to_upload[split] = data
                dataset = DatasetDict(datasets_to_upload)
            else:
                dataset = dataset_dict
            
            print(f"✅ データセット読み込み完了")
            for split in dataset:
                print(f"   {split}: {len(dataset[split]):,} サンプル")
            
        except Exception as e:
            import traceback
            print(f"エラー: データセットの読み込みに失敗しました: {e}")
            print("\nデバッグ情報:")
            print(traceback.format_exc())
            return
        
        # データセットカードの生成
        dataset_card = generate_dataset_card(args.dataset_name, dataset, args.input_path)
    
    # レガシーモード（後方互換性）
    elif args.dataset_type:
        print("⚠️  レガシーモード: 新規データセット生成。--input-pathの使用を推奨します。")
        
        builder = HuggingFaceDatasetBuilder()
        
        if args.dataset_type == "kanji" or args.dataset_type == "all":
            print(f"漢字読みデータセット生成中（学年: {args.grades or '全学年'}）...")
            dataset = builder.create_kanji_reading_dataset(
                num_samples_per_grade=1000,
                grades=args.grades or [1, 2, 3, 4, 5, 6],
                include_on_yomi=True,
                include_kun_yomi=True
            )
            dataset_card = generate_kanji_dataset_card(args.dataset_name, args.grades or [1, 2, 3, 4, 5, 6], dataset)
        
        
        elif args.dataset_type == "grpo":
            print("GRPO データセット生成中...")
            dataset = builder.create_grpo_dataset(
                num_groups=1000,
                group_size=4
            )
            dataset_card = generate_dataset_card(args.dataset_name, dataset, "generated")
        
        elif args.dataset_type == "chat":
            print("チャット形式データセット生成中...")
            dataset = builder.create_chat_format_dataset(
                num_samples=5000
            )
            dataset_card = generate_dataset_card(args.dataset_name, dataset, "generated")
        
        else:  # "all"
            print("全タイプのデータセット生成はサポートされていません。特定のタイプを選択してください。")
            return
    
    else:
        parser.error("--input-pathまたは--dataset-typeのいずれかを指定してください")
        return
    
    # リポジトリ作成
    print(f"\n📤 リポジトリ作成中: {repo_id}")
    try:
        create_repo(
            repo_id=repo_id,
            token=token,
            private=args.private,
            repo_type="dataset",
            exist_ok=True
        )
    except Exception as e:
        print(f"リポジトリが既に存在するか、エラーが発生しました: {e}")
    
    # データセットをアップロード
    print("📤 データセットをHugging Face Hubにアップロード中...")
    try:
        dataset.push_to_hub(
            repo_id,
            token=token,
            private=args.private,
            commit_message="Upload dataset via Nihongo DoJo"
        )
        
        # READMEを更新
        api = HfApi()
        api.upload_file(
            path_or_fileobj=dataset_card.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            token=token,
            commit_message="Update dataset card"
        )
        
        print(f"\n✅ データセットが正常にアップロードされました: https://huggingface.co/datasets/{repo_id}")
        
    except Exception as e:
        print(f"\nエラー: アップロードに失敗しました: {e}")
        print("トークンの権限やインターネット接続を確認してください。")


if __name__ == "__main__":
    main()