#!/usr/bin/env python3
"""
Backend API Testing for Idea Logger App
Tests all backend functionality according to test_result.md
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://6f2ff41c-052c-4d54-87f1-08a3d77b02b7.preview.emergentagent.com/api"

class IdeaLoggerTester:
    def __init__(self):
        self.session = requests.Session()
        self.created_categories = []
        self.created_ideas = []
        self.test_results = {
            "category_management": {"passed": 0, "failed": 0, "errors": []},
            "ideas_management": {"passed": 0, "failed": 0, "errors": []},
            "search_filtering": {"passed": 0, "failed": 0, "errors": []},
            "statistics": {"passed": 0, "failed": 0, "errors": []}
        }

    def log_result(self, test_category, test_name, success, error_msg=None):
        """Log test results"""
        if success:
            self.test_results[test_category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[test_category]["failed"] += 1
            self.test_results[test_category]["errors"].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")

    def test_category_management(self):
        """Test Category Management API"""
        print("\n🧪 Testing Category Management API...")
        
        # Test 1: Create categories
        categories_data = [
            {"name": "Product Ideas", "color": "#3b82f6"},
            {"name": "Business Strategy", "color": "#10b981"},
            {"name": "Personal Projects", "color": "#f59e0b"},
            {"name": "Research Topics", "color": "#ef4444"}
        ]
        
        for cat_data in categories_data:
            try:
                response = self.session.post(f"{BASE_URL}/categories", json=cat_data)
                if response.status_code == 200:
                    category = response.json()
                    self.created_categories.append(category)
                    self.log_result("category_management", f"Create category '{cat_data['name']}'", True)
                    
                    # Verify response structure
                    required_fields = ["id", "name", "color", "created_at"]
                    if all(field in category for field in required_fields):
                        self.log_result("category_management", f"Category '{cat_data['name']}' has correct structure", True)
                    else:
                        self.log_result("category_management", f"Category '{cat_data['name']}' missing required fields", False, f"Missing fields: {[f for f in required_fields if f not in category]}")
                else:
                    self.log_result("category_management", f"Create category '{cat_data['name']}'", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("category_management", f"Create category '{cat_data['name']}'", False, str(e))

        # Test 2: Get all categories
        try:
            response = self.session.get(f"{BASE_URL}/categories")
            if response.status_code == 200:
                categories = response.json()
                if len(categories) >= len(self.created_categories):
                    self.log_result("category_management", "Get all categories", True)
                    
                    # Verify created categories are in the list
                    created_ids = {cat["id"] for cat in self.created_categories}
                    fetched_ids = {cat["id"] for cat in categories}
                    if created_ids.issubset(fetched_ids):
                        self.log_result("category_management", "All created categories returned in list", True)
                    else:
                        self.log_result("category_management", "All created categories returned in list", False, "Some created categories missing from list")
                else:
                    self.log_result("category_management", "Get all categories", False, f"Expected at least {len(self.created_categories)} categories, got {len(categories)}")
            else:
                self.log_result("category_management", "Get all categories", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("category_management", "Get all categories", False, str(e))

        # Test 3: Delete category (soft delete)
        if self.created_categories:
            category_to_delete = self.created_categories[0]
            try:
                response = self.session.delete(f"{BASE_URL}/categories/{category_to_delete['id']}")
                if response.status_code == 200:
                    self.log_result("category_management", "Delete category", True)
                    
                    # Verify category is no longer in the list
                    response = self.session.get(f"{BASE_URL}/categories")
                    if response.status_code == 200:
                        categories = response.json()
                        deleted_ids = {cat["id"] for cat in categories}
                        if category_to_delete["id"] not in deleted_ids:
                            self.log_result("category_management", "Deleted category not in list (soft delete working)", True)
                        else:
                            self.log_result("category_management", "Deleted category not in list (soft delete working)", False, "Deleted category still appears in list")
                else:
                    self.log_result("category_management", "Delete category", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("category_management", "Delete category", False, str(e))

    def test_ideas_management(self):
        """Test Ideas Management API"""
        print("\n🧪 Testing Ideas Management API...")
        
        # Test 1: Create ideas
        ideas_data = [
            {
                "title": "AI-Powered Task Manager",
                "content": "<h2>Revolutionary Task Management</h2><p>An intelligent task manager that uses <strong>machine learning</strong> to predict task completion times and automatically prioritize work based on deadlines and importance.</p><ul><li>Smart scheduling algorithms</li><li>Natural language processing for task creation</li><li>Integration with calendar apps</li></ul>",
                "category_id": self.created_categories[1]["id"] if len(self.created_categories) > 1 else None,
                "tags": ["AI", "productivity", "machine-learning", "automation"]
            },
            {
                "title": "Sustainable Urban Farming Platform",
                "content": "<h2>Green City Initiative</h2><p>A comprehensive platform connecting urban farmers with <em>local communities</em> to promote sustainable food production in cities.</p><p>Key features:</p><ol><li>Community garden mapping</li><li>Resource sharing marketplace</li><li>Educational workshops and tutorials</li><li>Crop planning and tracking tools</li></ol>",
                "category_id": self.created_categories[2]["id"] if len(self.created_categories) > 2 else None,
                "tags": ["sustainability", "urban-farming", "community", "environment"]
            },
            {
                "title": "Virtual Reality Learning Experiences",
                "content": "<h2>Immersive Education</h2><p>Create <strong>immersive VR experiences</strong> for educational content, allowing students to explore historical events, scientific concepts, and complex systems in three-dimensional space.</p><p>Applications include:</p><ul><li>Historical recreations</li><li>Scientific simulations</li><li>Language immersion environments</li><li>Medical training scenarios</li></ul>",
                "category_id": self.created_categories[3]["id"] if len(self.created_categories) > 3 else None,
                "tags": ["VR", "education", "immersive", "technology", "learning"]
            }
        ]
        
        for idea_data in ideas_data:
            try:
                response = self.session.post(f"{BASE_URL}/ideas", json=idea_data)
                if response.status_code == 200:
                    idea = response.json()
                    self.created_ideas.append(idea)
                    self.log_result("ideas_management", f"Create idea '{idea_data['title']}'", True)
                    
                    # Verify response structure
                    required_fields = ["id", "title", "content", "tags", "is_archived", "created_at", "updated_at"]
                    if all(field in idea for field in required_fields):
                        self.log_result("ideas_management", f"Idea '{idea_data['title']}' has correct structure", True)
                    else:
                        self.log_result("ideas_management", f"Idea '{idea_data['title']}' missing required fields", False, f"Missing fields: {[f for f in required_fields if f not in idea]}")
                else:
                    self.log_result("ideas_management", f"Create idea '{idea_data['title']}'", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("ideas_management", f"Create idea '{idea_data['title']}'", False, str(e))

        # Test 2: Get all ideas
        try:
            response = self.session.get(f"{BASE_URL}/ideas")
            if response.status_code == 200:
                ideas = response.json()
                if len(ideas) >= len(self.created_ideas):
                    self.log_result("ideas_management", "Get all ideas", True)
                    
                    # Verify created ideas are in the list
                    created_ids = {idea["id"] for idea in self.created_ideas}
                    fetched_ids = {idea["id"] for idea in ideas}
                    if created_ids.issubset(fetched_ids):
                        self.log_result("ideas_management", "All created ideas returned in list", True)
                    else:
                        self.log_result("ideas_management", "All created ideas returned in list", False, "Some created ideas missing from list")
                else:
                    self.log_result("ideas_management", "Get all ideas", False, f"Expected at least {len(self.created_ideas)} ideas, got {len(ideas)}")
            else:
                self.log_result("ideas_management", "Get all ideas", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("ideas_management", "Get all ideas", False, str(e))

        # Test 3: Get single idea
        if self.created_ideas:
            idea_to_get = self.created_ideas[0]
            try:
                response = self.session.get(f"{BASE_URL}/ideas/{idea_to_get['id']}")
                if response.status_code == 200:
                    idea = response.json()
                    if idea["id"] == idea_to_get["id"]:
                        self.log_result("ideas_management", "Get single idea by ID", True)
                    else:
                        self.log_result("ideas_management", "Get single idea by ID", False, "Returned idea ID doesn't match requested ID")
                else:
                    self.log_result("ideas_management", "Get single idea by ID", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("ideas_management", "Get single idea by ID", False, str(e))

        # Test 4: Update idea
        if self.created_ideas:
            idea_to_update = self.created_ideas[0]
            update_data = {
                "title": "AI-Powered Task Manager (Updated)",
                "content": "<h2>Revolutionary Task Management - Enhanced Version</h2><p>Updated with new features and improvements.</p>",
                "tags": ["AI", "productivity", "machine-learning", "automation", "updated"]
            }
            try:
                response = self.session.put(f"{BASE_URL}/ideas/{idea_to_update['id']}", json=update_data)
                if response.status_code == 200:
                    updated_idea = response.json()
                    if updated_idea["title"] == update_data["title"] and "updated" in updated_idea["tags"]:
                        self.log_result("ideas_management", "Update idea", True)
                        # Update our local copy
                        self.created_ideas[0] = updated_idea
                    else:
                        self.log_result("ideas_management", "Update idea", False, "Updated idea doesn't reflect changes")
                else:
                    self.log_result("ideas_management", "Update idea", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("ideas_management", "Update idea", False, str(e))

        # Test 5: Archive/unarchive idea
        if self.created_ideas:
            idea_to_archive = self.created_ideas[1] if len(self.created_ideas) > 1 else self.created_ideas[0]
            try:
                # Archive the idea
                response = self.session.patch(f"{BASE_URL}/ideas/{idea_to_archive['id']}/archive")
                if response.status_code == 200:
                    self.log_result("ideas_management", "Archive idea", True)
                    
                    # Verify idea is archived by getting it
                    response = self.session.get(f"{BASE_URL}/ideas/{idea_to_archive['id']}")
                    if response.status_code == 200:
                        archived_idea = response.json()
                        if archived_idea["is_archived"]:
                            self.log_result("ideas_management", "Idea correctly marked as archived", True)
                            
                            # Unarchive the idea
                            response = self.session.patch(f"{BASE_URL}/ideas/{idea_to_archive['id']}/archive")
                            if response.status_code == 200:
                                self.log_result("ideas_management", "Unarchive idea", True)
                                
                                # Verify idea is unarchived
                                response = self.session.get(f"{BASE_URL}/ideas/{idea_to_archive['id']}")
                                if response.status_code == 200:
                                    unarchived_idea = response.json()
                                    if not unarchived_idea["is_archived"]:
                                        self.log_result("ideas_management", "Idea correctly marked as unarchived", True)
                                    else:
                                        self.log_result("ideas_management", "Idea correctly marked as unarchived", False, "Idea still marked as archived")
                        else:
                            self.log_result("ideas_management", "Idea correctly marked as archived", False, "Idea not marked as archived")
                else:
                    self.log_result("ideas_management", "Archive idea", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("ideas_management", "Archive idea", False, str(e))

        # Test 6: Delete idea (soft delete)
        if len(self.created_ideas) > 1:
            idea_to_delete = self.created_ideas[-1]  # Delete the last one
            try:
                response = self.session.delete(f"{BASE_URL}/ideas/{idea_to_delete['id']}")
                if response.status_code == 200:
                    self.log_result("ideas_management", "Delete idea", True)
                    
                    # Verify idea is no longer in the list
                    response = self.session.get(f"{BASE_URL}/ideas")
                    if response.status_code == 200:
                        ideas = response.json()
                        deleted_ids = {idea["id"] for idea in ideas}
                        if idea_to_delete["id"] not in deleted_ids:
                            self.log_result("ideas_management", "Deleted idea not in list (soft delete working)", True)
                        else:
                            self.log_result("ideas_management", "Deleted idea not in list (soft delete working)", False, "Deleted idea still appears in list")
                else:
                    self.log_result("ideas_management", "Delete idea", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("ideas_management", "Delete idea", False, str(e))

    def test_search_and_filtering(self):
        """Test Search and Filtering functionality"""
        print("\n🧪 Testing Search and Filtering...")
        
        # Test 1: Search by title
        try:
            response = self.session.get(f"{BASE_URL}/ideas", params={"search": "AI-Powered"})
            if response.status_code == 200:
                ideas = response.json()
                if any("AI-Powered" in idea["title"] for idea in ideas):
                    self.log_result("search_filtering", "Search by title", True)
                else:
                    self.log_result("search_filtering", "Search by title", False, "No matching ideas found in search results")
            else:
                self.log_result("search_filtering", "Search by title", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("search_filtering", "Search by title", False, str(e))

        # Test 2: Search by content
        try:
            response = self.session.get(f"{BASE_URL}/ideas", params={"search": "machine learning"})
            if response.status_code == 200:
                ideas = response.json()
                if any("machine learning" in idea["content"].lower() for idea in ideas):
                    self.log_result("search_filtering", "Search by content", True)
                else:
                    self.log_result("search_filtering", "Search by content", False, "No matching ideas found in search results")
            else:
                self.log_result("search_filtering", "Search by content", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("search_filtering", "Search by content", False, str(e))

        # Test 3: Search by tags
        try:
            response = self.session.get(f"{BASE_URL}/ideas", params={"search": "sustainability"})
            if response.status_code == 200:
                ideas = response.json()
                if any("sustainability" in idea["tags"] for idea in ideas):
                    self.log_result("search_filtering", "Search by tags", True)
                else:
                    self.log_result("search_filtering", "Search by tags", False, "No matching ideas found in search results")
            else:
                self.log_result("search_filtering", "Search by tags", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("search_filtering", "Search by tags", False, str(e))

        # Test 4: Filter by category
        if len(self.created_categories) > 1:
            category_id = self.created_categories[1]["id"]
            try:
                response = self.session.get(f"{BASE_URL}/ideas", params={"category_id": category_id})
                if response.status_code == 200:
                    ideas = response.json()
                    if all(idea["category_id"] == category_id for idea in ideas if idea["category_id"]):
                        self.log_result("search_filtering", "Filter by category", True)
                    else:
                        self.log_result("search_filtering", "Filter by category", False, "Results contain ideas from other categories")
                else:
                    self.log_result("search_filtering", "Filter by category", False, f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_result("search_filtering", "Filter by category", False, str(e))

        # Test 5: Filter by archived status (false)
        try:
            response = self.session.get(f"{BASE_URL}/ideas", params={"archived": "false"})
            if response.status_code == 200:
                ideas = response.json()
                if all(not idea["is_archived"] for idea in ideas):
                    self.log_result("search_filtering", "Filter by archived=false", True)
                else:
                    self.log_result("search_filtering", "Filter by archived=false", False, "Results contain archived ideas")
            else:
                self.log_result("search_filtering", "Filter by archived=false", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("search_filtering", "Filter by archived=false", False, str(e))

        # Test 6: Filter by archived status (true)
        try:
            response = self.session.get(f"{BASE_URL}/ideas", params={"archived": "true"})
            if response.status_code == 200:
                ideas = response.json()
                if all(idea["is_archived"] for idea in ideas):
                    self.log_result("search_filtering", "Filter by archived=true", True)
                else:
                    self.log_result("search_filtering", "Filter by archived=true", False, "Results contain non-archived ideas")
            else:
                self.log_result("search_filtering", "Filter by archived=true", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("search_filtering", "Filter by archived=true", False, str(e))

    def test_statistics(self):
        """Test Statistics API"""
        print("\n🧪 Testing Statistics API...")
        
        try:
            response = self.session.get(f"{BASE_URL}/stats")
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_ideas", "active_ideas", "archived_ideas", "total_categories"]
                
                if all(field in stats for field in required_fields):
                    self.log_result("statistics", "Get statistics - correct structure", True)
                    
                    # Verify statistics make sense
                    if (stats["total_ideas"] == stats["active_ideas"] + stats["archived_ideas"] and
                        stats["total_ideas"] >= 0 and stats["total_categories"] >= 0):
                        self.log_result("statistics", "Statistics calculations are consistent", True)
                    else:
                        self.log_result("statistics", "Statistics calculations are consistent", False, 
                                      f"Inconsistent stats: total={stats['total_ideas']}, active={stats['active_ideas']}, archived={stats['archived_ideas']}")
                    
                    print(f"📊 Current Statistics:")
                    print(f"   Total Ideas: {stats['total_ideas']}")
                    print(f"   Active Ideas: {stats['active_ideas']}")
                    print(f"   Archived Ideas: {stats['archived_ideas']}")
                    print(f"   Total Categories: {stats['total_categories']}")
                    
                else:
                    self.log_result("statistics", "Get statistics - correct structure", False, 
                                  f"Missing fields: {[f for f in required_fields if f not in stats]}")
            else:
                self.log_result("statistics", "Get statistics", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_result("statistics", "Get statistics", False, str(e))

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests for Idea Logger App")
        print(f"🌐 Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Run tests in order
        self.test_category_management()
        self.test_ideas_management()
        self.test_search_and_filtering()
        self.test_statistics()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.replace('_', ' ').title()}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  ❌ {error}")
        
        print(f"\nOverall: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 All backend tests passed!")
            return True
        else:
            print(f"⚠️  {total_failed} tests failed")
            return False

if __name__ == "__main__":
    tester = IdeaLoggerTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)