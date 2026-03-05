"""
🤖 LearningAgent
Analyzes git history and learns from previous commits to suggest improvements.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any
import asyncio
import subprocess
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LearningAgent:
    """Learns from git commit history and suggests improvements"""
    
    def __init__(self):
        self.name = "LearningAgent"
        self.target_dirs = ["."]
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.patterns_db = {}
    
    async def run(self) -> Dict[str, Any]:
        self.logger.info("🧠 Starting learning analysis...")
        results = {
            "commits_analyzed": 0,
            "patterns_identified": [],
            "suggestions_generated": [],
            "learning_insights": [],
            "errors": []
        }
        
        try:
            # Analyze recent git commits
            commits = await self._analyze_git_history()
            results["commits_analyzed"] = len(commits)
            
            if commits:
                # Identify recurring patterns
                patterns = await self._identify_patterns(commits)
                results["patterns_identified"] = patterns
                
                # Generate improvement suggestions
                suggestions = await self._generate_suggestions(patterns)
                results["suggestions_generated"] = suggestions
                
                # Extract learning insights
                insights = await self._extract_insights(commits)
                results["learning_insights"] = insights
            
            self.logger.info(
                f"✅ Learning analysis completed: "
                f"{len(results['patterns_identified'])} patterns, "
                f"{len(results['suggestions_generated'])} suggestions"
            )
            results["status"] = "success"
            
        except Exception as e:
            self.logger.error(f"💥 LearningAgent crashed: {str(e)}")
            results["errors"].append(str(e))
            results["status"] = "crashed"
            
        return results
    
    async def _analyze_git_history(self) -> List[Dict]:
        """Analyze recent git commit history"""
        try:
            # Get last 20 commits
            cmd = [
                "git", "log", "-20", 
                "--pretty=format:%H|%an|%ad|%s", 
                "--date=iso"
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                commits = []
                lines = stdout.decode().strip().split('\n')
                
                for line in lines:
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) == 4:
                            commit_hash, author, date_str, message = parts
                            commits.append({
                                "hash": commit_hash.strip(),
                                "author": author.strip(),
                                "date": date_str.strip(),
                                "message": message.strip(),
                                "timestamp": datetime.fromisoformat(
                                    date_str.strip().replace(' ', 'T')
                                )
                            })
                
                return commits
            else:
                self.logger.warning(f"Git log failed: {stderr.decode()}")
                return []
                
        except FileNotFoundError:
            self.logger.info("Git not available, skipping...")
            return []
        except Exception as e:
            self.logger.error(f"Git analysis failed: {str(e)}")
            return []
    
    async def _identify_patterns(self, commits: List[Dict]) -> List[Dict]:
        """Identify recurring patterns in commit messages"""
        patterns = []
        
        try:
            # Count commit message keywords
            keyword_counts = {}
            fix_keywords = ["fix", "bug", "error", "issue", "problem"]
            feature_keywords = ["add", "implement", "create", "new"]
            refactor_keywords = ["refactor", "cleanup", "optimize", "improve"]
            
            for commit in commits:
                message = commit["message"].lower()
                
                # Categorize commits
                category = "other"
                if any(keyword in message for keyword in fix_keywords):
                    category = "bug_fix"
                elif any(keyword in message for keyword in feature_keywords):
                    category = "feature"
                elif any(keyword in message for keyword in refactor_keywords):
                    category = "refactor"
                
                keyword_counts[category] = keyword_counts.get(category, 0) + 1
            
            # Generate patterns
            for category, count in keyword_counts.items():
                if count > 2:  # Significant pattern
                    patterns.append({
                        "type": "commit_category",
                        "category": category,
                        "frequency": count,
                        "percentage": round((count / len(commits)) * 100, 1)
                    })
            
            # Look for file modification patterns
            file_modifications = await self._analyze_file_changes(commits[:10])
            patterns.extend(file_modifications)
            
        except Exception as e:
            self.logger.error(f"Pattern identification failed: {str(e)}")
            
        return patterns
    
    async def _analyze_file_changes(self, recent_commits: List[Dict]) -> List[Dict]:
        """Analyze which files are frequently modified"""
        file_changes = {}
        
        try:
            for commit in recent_commits:
                cmd = ["git", "show", "--name-only", commit["hash"]]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    lines = stdout.decode().split('\n')
                    for line in lines:
                        if line and not line.startswith('commit'):
                            file_path = line.strip()
                            if file_path.endswith('.py') or file_path.endswith('.ts'):
                                file_changes[file_path] = file_changes.get(file_path, 0) + 1
            
            # Convert to patterns
            patterns = []
            for file_path, count in file_changes.items():
                if count > 1:
                    patterns.append({
                        "type": "file_modification",
                        "file": file_path,
                        "modifications": count,
                        "hotspot": count > 3
                    })
                    
            return patterns[:10]  # Top 10 hotspots
            
        except Exception as e:
            self.logger.error(f"File change analysis failed: {str(e)}")
            return []
    
    async def _generate_suggestions(self, patterns: List[Dict]) -> List[str]:
        """Generate improvement suggestions based on patterns"""
        suggestions = []
        
        try:
            for pattern in patterns:
                if pattern["type"] == "commit_category":
                    if pattern["category"] == "bug_fix" and pattern["percentage"] > 30:
                        suggestions.append(
                            "⚠️ High bug fix ratio detected. "
                            "Consider adding more unit tests or improving code review process."
                        )
                    elif pattern["category"] == "refactor" and pattern["percentage"] > 25:
                        suggestions.append(
                            "🔄 Frequent refactoring detected. "
                            "Consider establishing coding standards and automated linting."
                        )
                        
                elif pattern["type"] == "file_modification":
                    if pattern["hotspot"]:
                        suggestions.append(
                            f"🔥 Hotspot detected: {pattern['file']} modified {pattern['modifications']} times. "
                            "Consider modularizing this component or adding better abstractions."
                        )
                    elif pattern["modifications"] > 2:
                        suggestions.append(
                            f"📈 {pattern['file']} frequently modified ({pattern['modifications']} times). "
                            "Review for potential design improvements."
                        )
            
            # General suggestions based on commit frequency
            if len(patterns) > 0:
                suggestions.append(
                    "📊 Consider implementing automated code quality checks "
                    "to reduce manual fixes."
                )
                suggestions.append(
                    "🚀 Frequent commits suggest active development. "
                    "Ensure proper documentation and testing coverage."
                )
                
        except Exception as e:
            self.logger.error(f"Suggestion generation failed: {str(e)}")
            
        return suggestions
    
    async def _extract_insights(self, commits: List[Dict]) -> List[str]:
        """Extract learning insights from commit history"""
        insights = []
        
        try:
            # Author contribution analysis
            authors = {}
            for commit in commits:
                author = commit["author"]
                authors[author] = authors.get(author, 0) + 1
            
            if len(authors) == 1:
                insights.append("👤 Single contributor detected. Consider peer review process.")
            elif len(authors) > 3:
                insights.append("👥 Multiple contributors active. Good collaboration signs.")
            
            # Commit frequency analysis
            if commits:
                first_commit = min(c["timestamp"] for c in commits)
                last_commit = max(c["timestamp"] for c in commits)
                days_span = (last_commit - first_commit).days
                
                if days_span > 0:
                    commits_per_day = len(commits) / days_span
                    if commits_per_day > 2:
                        insights.append("⚡ High commit frequency. Rapid development pace.")
                    elif commits_per_day < 0.5:
                        insights.append("🐢 Low commit frequency. Consider more frequent integration.")
            
            # Message quality insights
            short_messages = sum(1 for c in commits if len(c["message"]) < 20)
            if short_messages > len(commits) * 0.3:
                insights.append("📝 Many short commit messages. Consider more descriptive messages.")
                
        except Exception as e:
            self.logger.error(f"Insight extraction failed: {str(e)}")
            
        return insights