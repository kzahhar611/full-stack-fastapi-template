#!/usr/bin/env python3
"""
TenderWise AI - Performance Testing Script
Comprehensive performance testing and benchmarking
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Tuple
import json
import argparse
from concurrent.futures import ThreadPoolExecutor
import sys

class PerformanceTester:
    """
    Comprehensive performance testing for TenderWise AI API
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        
    async def setup(self):
        """Setup test session and authentication"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate to get token
        try:
            login_data = {
                "email": "rfp@kzahhar.com",
                "password": "password123"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print("✅ Authentication successful")
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Setup failed: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def test_endpoint(self, 
                           endpoint: str, 
                           method: str = "GET", 
                           data: Dict = None,
                           count: int = 10) -> Dict:
        """Test a single endpoint multiple times"""
        
        url = f"{self.base_url}{endpoint}"
        headers = self.get_headers()
        response_times = []
        status_codes = []
        errors = []
        
        print(f"\n🔍 Testing {method} {endpoint} ({count} requests)")
        
        for i in range(count):
            try:
                start_time = time.time()
                
                if method.upper() == "GET":
                    async with self.session.get(url, headers=headers) as response:
                        status_code = response.status
                        await response.text()  # Read response body
                elif method.upper() == "POST":
                    async with self.session.post(url, headers=headers, json=data) as response:
                        status_code = response.status
                        await response.text()
                else:
                    continue
                
                response_time = time.time() - start_time
                response_times.append(response_time)
                status_codes.append(status_code)
                
                if i % 10 == 0:
                    print(f"  Progress: {i}/{count}")
                    
            except Exception as e:
                errors.append(str(e))
                print(f"  Error in request {i}: {e}")
        
        # Calculate statistics
        if response_times:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "total_requests": count,
                "successful_requests": len(response_times),
                "failed_requests": len(errors),
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "median_response_time": statistics.median(response_times),
                "p95_response_time": self.percentile(response_times, 95),
                "p99_response_time": self.percentile(response_times, 99),
                "requests_per_second": len(response_times) / sum(response_times) if response_times else 0,
                "status_codes": dict(zip(*zip(*[(code, status_codes.count(code)) for code in set(status_codes)]))),
                "errors": errors[:5]  # First 5 errors
            }
        else:
            stats = {
                "endpoint": endpoint,
                "method": method,
                "total_requests": count,
                "successful_requests": 0,
                "failed_requests": len(errors),
                "errors": errors[:5]
            }
        
        return stats
    
    def percentile(self, data: List[float], p: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * p / 100
        f = int(k)
        c = k - f
        if f == len(sorted_data) - 1:
            return sorted_data[f]
        return sorted_data[f] * (1 - c) + sorted_data[f + 1] * c
    
    async def test_concurrent_load(self, 
                                  endpoint: str, 
                                  concurrent_users: int = 10,
                                  requests_per_user: int = 5) -> Dict:
        """Test concurrent load on an endpoint"""
        
        print(f"\n🔥 Load testing {endpoint} ({concurrent_users} concurrent users, {requests_per_user} requests each)")
        
        async def user_requests(user_id: int):
            user_stats = []
            for i in range(requests_per_user):
                try:
                    start_time = time.time()
                    async with self.session.get(
                        f"{self.base_url}{endpoint}",
                        headers=self.get_headers()
                    ) as response:
                        status_code = response.status
                        await response.text()
                    
                    response_time = time.time() - start_time
                    user_stats.append({
                        "user_id": user_id,
                        "request_id": i,
                        "response_time": response_time,
                        "status_code": status_code
                    })
                except Exception as e:
                    user_stats.append({
                        "user_id": user_id,
                        "request_id": i,
                        "error": str(e)
                    })
            return user_stats
        
        # Run concurrent users
        start_time = time.time()
        tasks = [user_requests(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Aggregate results
        all_requests = [req for user_results in results for req in user_results]
        successful_requests = [req for req in all_requests if "error" not in req]
        failed_requests = [req for req in all_requests if "error" in req]
        
        if successful_requests:
            response_times = [req["response_time"] for req in successful_requests]
            
            stats = {
                "endpoint": endpoint,
                "concurrent_users": concurrent_users,
                "requests_per_user": requests_per_user,
                "total_requests": len(all_requests),
                "successful_requests": len(successful_requests),
                "failed_requests": len(failed_requests),
                "total_test_time": total_time,
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "p95_response_time": self.percentile(response_times, 95),
                "p99_response_time": self.percentile(response_times, 99),
                "requests_per_second": len(successful_requests) / total_time,
                "success_rate": len(successful_requests) / len(all_requests) * 100
            }
        else:
            stats = {
                "endpoint": endpoint,
                "concurrent_users": concurrent_users,
                "total_requests": len(all_requests),
                "successful_requests": 0,
                "failed_requests": len(failed_requests),
                "success_rate": 0
            }
        
        return stats
    
    async def test_cache_performance(self) -> Dict:
        """Test cache hit/miss performance"""
        
        print("\n💾 Testing cache performance...")
        
        # Test endpoint that should be cached
        endpoint = "/api/v1/rfps/"
        cache_stats = {}
        
        # First request (cache miss)
        start_time = time.time()
        async with self.session.get(
            f"{self.base_url}{endpoint}",
            headers=self.get_headers()
        ) as response:
            first_response_time = time.time() - start_time
            await response.text()
        
        # Second request (should be cache hit)
        start_time = time.time()
        async with self.session.get(
            f"{self.base_url}{endpoint}",
            headers=self.get_headers()
        ) as response:
            second_response_time = time.time() - start_time
            await response.text()
        
        cache_stats = {
            "first_request_time": first_response_time,
            "second_request_time": second_response_time,
            "cache_improvement": ((first_response_time - second_response_time) / first_response_time) * 100,
            "cache_effective": second_response_time < first_response_time
        }
        
        return cache_stats
    
    async def run_comprehensive_test(self) -> Dict:
        """Run comprehensive performance test suite"""
        
        print("🚀 Starting TenderWise AI Performance Test Suite")
        print("=" * 60)
        
        test_results = {
            "test_timestamp": time.time(),
            "base_url": self.base_url,
            "endpoint_tests": [],
            "load_tests": [],
            "cache_test": {},
            "summary": {}
        }
        
        # Test individual endpoints
        endpoints_to_test = [
            ("/health", "GET"),
            ("/api/v1/rfps/", "GET"),
            ("/api/v1/rfps-enhanced/", "GET"),
            ("/api/v1/analytics/dashboard", "GET"),
            ("/api/v1/organizations/", "GET"),
        ]
        
        for endpoint, method in endpoints_to_test:
            try:
                stats = await self.test_endpoint(endpoint, method, count=20)
                test_results["endpoint_tests"].append(stats)
                
                # Print results
                if stats.get("successful_requests", 0) > 0:
                    print(f"  ✅ Avg: {stats['avg_response_time']:.3f}s, "
                          f"P95: {stats['p95_response_time']:.3f}s, "
                          f"RPS: {stats['requests_per_second']:.1f}")
                else:
                    print(f"  ❌ All requests failed")
                    
            except Exception as e:
                print(f"  ❌ Test failed: {e}")
        
        # Load tests
        load_test_endpoints = [
            "/health",
            "/api/v1/rfps/"
        ]
        
        for endpoint in load_test_endpoints:
            try:
                stats = await self.test_concurrent_load(endpoint, concurrent_users=5, requests_per_user=3)
                test_results["load_tests"].append(stats)
                
                if stats.get("successful_requests", 0) > 0:
                    print(f"  ✅ Success Rate: {stats['success_rate']:.1f}%, "
                          f"RPS: {stats['requests_per_second']:.1f}, "
                          f"Avg: {stats['avg_response_time']:.3f}s")
                else:
                    print(f"  ❌ Load test failed")
                    
            except Exception as e:
                print(f"  ❌ Load test failed: {e}")
        
        # Cache test
        try:
            cache_stats = await self.test_cache_performance()
            test_results["cache_test"] = cache_stats
            
            if cache_stats["cache_effective"]:
                print(f"  ✅ Cache improvement: {cache_stats['cache_improvement']:.1f}%")
            else:
                print(f"  ⚠️ Cache may not be working effectively")
                
        except Exception as e:
            print(f"  ❌ Cache test failed: {e}")
        
        # Generate summary
        successful_endpoint_tests = [t for t in test_results["endpoint_tests"] if t.get("successful_requests", 0) > 0]
        
        if successful_endpoint_tests:
            avg_response_times = [t["avg_response_time"] for t in successful_endpoint_tests]
            
            test_results["summary"] = {
                "total_endpoints_tested": len(test_results["endpoint_tests"]),
                "successful_endpoint_tests": len(successful_endpoint_tests),
                "overall_avg_response_time": statistics.mean(avg_response_times),
                "fastest_endpoint": min(successful_endpoint_tests, key=lambda x: x["avg_response_time"])["endpoint"],
                "slowest_endpoint": max(successful_endpoint_tests, key=lambda x: x["avg_response_time"])["endpoint"],
                "cache_working": test_results["cache_test"].get("cache_effective", False)
            }
        
        return test_results
    
    def print_summary(self, results: Dict):
        """Print test summary"""
        
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        summary = results.get("summary", {})
        
        if summary:
            print(f"✅ Endpoints tested: {summary['total_endpoints_tested']}")
            print(f"✅ Successful tests: {summary['successful_endpoint_tests']}")
            print(f"⚡ Overall avg response time: {summary.get('overall_avg_response_time', 0):.3f}s")
            print(f"🏃 Fastest endpoint: {summary.get('fastest_endpoint', 'N/A')}")
            print(f"🐌 Slowest endpoint: {summary.get('slowest_endpoint', 'N/A')}")
            print(f"💾 Cache working: {'✅ Yes' if summary.get('cache_working') else '❌ No'}")
        
        # Performance assessment
        avg_time = summary.get('overall_avg_response_time', 0)
        if avg_time < 0.1:
            grade = "🏆 EXCELLENT"
        elif avg_time < 0.5:
            grade = "✅ GOOD"
        elif avg_time < 1.0:
            grade = "⚠️ ACCEPTABLE"
        else:
            grade = "❌ NEEDS IMPROVEMENT"
        
        print(f"\n🎯 Performance Grade: {grade}")
        print("=" * 60)


async def main():
    parser = argparse.ArgumentParser(description="TenderWise AI Performance Testing")
    parser.add_argument("--url", default="http://localhost:8000", help="Base URL to test")
    parser.add_argument("--output", help="Output file for results (JSON)")
    parser.add_argument("--quick", action="store_true", help="Run quick test with fewer requests")
    
    args = parser.parse_args()
    
    tester = PerformanceTester(args.url)
    
    try:
        await tester.setup()
        
        if tester.auth_token is None:
            print("❌ Cannot run tests without authentication")
            return
        
        results = await tester.run_comprehensive_test()
        tester.print_summary(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Results saved to: {args.output}")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        sys.exit(1)
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())