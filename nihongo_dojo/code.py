#!/usr/bin/env python3
"""
Main CLI entry point for Nihongo DoJo
Provides unified interface for dataset generation and HuggingFace upload
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog='nihongo-dojo',
        description='Nihongo DoJo - Japanese Language Training Dataset Generator for GRPO'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate GRPO datasets')
    generate_parser.add_argument('--preset', choices=['small', 'medium', 'large', 'extra_large'],
                               help='Use preset dataset size')
    generate_parser.add_argument('--custom-size', type=int, help='Custom dataset size')
    generate_parser.add_argument('--grades', nargs='+', type=int, choices=range(1, 10),
                               help='Kanji grades to include (1-6 elementary, 7-9 junior high)')
    generate_parser.add_argument('--tasks', nargs='+', help='Specific task types to generate')
    generate_parser.add_argument('--task-distribution', type=str,
                               help='Task distribution (e.g., "basic:0.6,advanced:0.3,cultural:0.1")')
    generate_parser.add_argument('--output-dir', type=str, default='./datasets',
                               help='Output directory for datasets')
    generate_parser.add_argument('--output-format', choices=['json', 'jsonl', 'parquet', 'csv'],
                               default='jsonl', help='Output format')
    generate_parser.add_argument('--compress', action='store_true', help='Compress output files')
    generate_parser.add_argument('--num-workers', type=int, help='Number of parallel workers')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', help='Upload dataset to HuggingFace')
    upload_parser.add_argument('--input-path', required=True, help='Path to dataset directory')
    upload_parser.add_argument('--dataset-name', required=True, help='Name for HuggingFace dataset')
    upload_parser.add_argument('--organization', help='HuggingFace organization')
    upload_parser.add_argument('--private', action='store_true', help='Make dataset private')
    upload_parser.add_argument('--token', help='HuggingFace API token')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == 'generate':
        # Import and run generate_datasets
        from generate_datasets import main as generate_main
        
        # Build command line args for generate_datasets
        cmd_args = []
        if args.preset:
            cmd_args.extend(['--preset', args.preset])
        if args.custom_size:
            cmd_args.extend(['--custom-size', str(args.custom_size)])
        if args.grades:
            cmd_args.extend(['--grades'] + [str(g) for g in args.grades])
        if args.tasks:
            cmd_args.extend(['--tasks'] + args.tasks)
        if args.task_distribution:
            cmd_args.extend(['--task-distribution', args.task_distribution])
        if args.output_dir:
            cmd_args.extend(['--output-dir', args.output_dir])
        if args.output_format:
            cmd_args.extend(['--output-format', args.output_format])
        if args.compress:
            cmd_args.append('--compress')
        if args.num_workers:
            cmd_args.extend(['--num-workers', str(args.num_workers)])
        
        # Override sys.argv for generate_datasets
        sys.argv = ['generate_datasets.py'] + cmd_args
        generate_main()
        
    elif args.command == 'upload':
        # Import and run upload_to_huggingface
        from upload_to_huggingface import main as upload_main
        
        # Build command line args for upload_to_huggingface
        cmd_args = [
            '--input-path', args.input_path,
            '--dataset-name', args.dataset_name
        ]
        if args.organization:
            cmd_args.extend(['--organization', args.organization])
        if args.private:
            cmd_args.append('--private')
        if args.token:
            cmd_args.extend(['--token', args.token])
        
        # Override sys.argv for upload_to_huggingface
        sys.argv = ['upload_to_huggingface.py'] + cmd_args
        upload_main()

if __name__ == '__main__':
    main()