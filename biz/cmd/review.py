import os

import openai
import pathspec

# 支持的开发语言
SUPPORTED_LANGUAGES = ["java", "python", "php"]


def parse_arguments():
    """使用交互方式获取用户输入"""
    while True:
        language = input("请选择开发语言 (java/python/php): ").strip().lower()
        if language in ["java", "python", "php"]:
            break
        print("❌ 请输入有效的语言: java, python, php")

    while True:
        directory = input("请输入代码项目的根目录路径: ").strip()
        if os.path.isdir(directory):
            break
        print("❌ 目录不存在，请输入有效路径")

    return language, directory


def load_gitignore_patterns(project_dir):
    """读取 .gitignore 规则"""
    gitignore_path = os.path.join(project_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns = f.readlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return None


def scan_directory(directory, ignore_spec, prefix=""):
    """以 tree 命令的格式展示目录结构，并应用 .gitignore 规则"""
    entries = sorted(os.listdir(directory))  # 排序保证输出一致
    entries = [e for e in entries if not e.startswith(".")]  # 忽略隐藏文件

    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        relative_path = os.path.relpath(path, start=directory)

        # 检查是否匹配 .gitignore 规则
        if ignore_spec and ignore_spec.match_file(relative_path):
            continue  # 忽略匹配的文件/目录

        is_last = (index == len(entries) - 1)
        connector = "└── " if is_last else "├── "
        print(prefix + connector + entry)

        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            scan_directory(path, ignore_spec, new_prefix)

def load_gitignore_patterns(project_dir):
    """读取 .gitignore 规则"""
    gitignore_path = os.path.join(project_dir, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            patterns = f.readlines()
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)
    return None




if __name__ == "__main__":
    # language, directory = parse_arguments()
    project_dir = "."  # 当前目录
    ignore_spec = load_gitignore_patterns(project_dir)
    scan_directory(project_dir, ignore_spec)
