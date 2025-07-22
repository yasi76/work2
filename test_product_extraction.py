#!/usr/bin/env python3
"""
Unit tests for product extraction methods
Tests key functionality like product name validation, fuzzy matching, and classification
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extract_products import ProductExtractor, URLNormalizer, HTMLCache


class TestURLNormalizer(unittest.TestCase):
    """Test URL normalization"""
    
    def setUp(self):
        self.normalizer = URLNormalizer()
    
    def test_remove_www(self):
        """Test www prefix removal"""
        self.assertEqual(
            self.normalizer.normalize("https://www.example.com"),
            "https://example.com"
        )
    
    def test_remove_trailing_slash(self):
        """Test trailing slash removal"""
        self.assertEqual(
            self.normalizer.normalize("https://example.com/"),
            "https://example.com"
        )
    
    def test_lowercase_domain(self):
        """Test domain lowercasing"""
        self.assertEqual(
            self.normalizer.normalize("https://EXAMPLE.COM"),
            "https://example.com"
        )
    
    def test_preserve_path(self):
        """Test path preservation"""
        self.assertEqual(
            self.normalizer.normalize("https://example.com/products"),
            "https://example.com/products"
        )
    
    def test_complex_normalization(self):
        """Test complex URL normalization"""
        self.assertEqual(
            self.normalizer.normalize("https://WWW.Example.COM/path/?query=1#fragment"),
            "https://example.com/path"
        )


class TestProductNameValidation(unittest.TestCase):
    """Test product name validation"""
    
    def setUp(self):
        self.extractor = ProductExtractor(use_cache=False)
    
    def test_generic_names_rejected(self):
        """Test that generic names are rejected"""
        generic_names = ["our app", "the platform", "unsere app", "our solution"]
        
        for name in generic_names:
            is_valid, confidence = self.extractor._is_likely_product_name(name)
            self.assertFalse(is_valid)
            self.assertEqual(confidence, 0.0)
    
    def test_valid_product_names(self):
        """Test valid product names"""
        valid_names = [
            ("HealthTracker Pro", True),
            ("MediCare Assistant", True),
            ("FitBit", True),
            ("AI Diagnostics Platform", True)
        ]
        
        for name, expected in valid_names:
            is_valid, confidence = self.extractor._is_likely_product_name(name)
            self.assertEqual(is_valid, expected)
            self.assertGreater(confidence, 0.5)
    
    def test_confidence_scoring(self):
        """Test confidence scoring logic"""
        # Very short name
        is_valid, confidence = self.extractor._is_likely_product_name("AI")
        self.assertLess(confidence, 0.5)
        
        # Very long name
        is_valid, confidence = self.extractor._is_likely_product_name(
            "This is a very long product name that should have lower confidence score"
        )
        self.assertLess(confidence, 0.5)
        
        # Trademark symbol boosts confidence
        is_valid, confidence1 = self.extractor._is_likely_product_name("Product")
        is_valid, confidence2 = self.extractor._is_likely_product_name("Product®")
        self.assertGreater(confidence2, confidence1)
    
    def test_sentence_patterns(self):
        """Test sentence pattern detection"""
        sentences = [
            "This is our product",
            "We are the best",
            "Our amazing solution"
        ]
        
        for sentence in sentences:
            is_valid, confidence = self.extractor._is_likely_product_name(sentence)
            self.assertLess(confidence, 0.4)


class TestFuzzyMatching(unittest.TestCase):
    """Test fuzzy matching functionality"""
    
    def setUp(self):
        self.extractor = ProductExtractor(use_cache=False)
    
    def test_exact_duplicates(self):
        """Test exact duplicate removal"""
        products = [
            {'name': 'HealthApp', 'confidence': 0.8},
            {'name': 'HealthApp', 'confidence': 0.7},
            {'name': 'MediTool', 'confidence': 0.9}
        ]
        
        result = self.extractor._fuzzy_match_products(products)
        self.assertEqual(len(result), 2)
        
        # Should keep the one with higher confidence
        health_app = next(p for p in result if p['name'] == 'HealthApp')
        self.assertEqual(health_app['confidence'], 0.8)
    
    def test_similar_names(self):
        """Test similar name matching"""
        products = [
            {'name': 'Health Tracker', 'confidence': 0.8},
            {'name': 'HealthTracker', 'confidence': 0.7},
            {'name': 'Health-Tracker', 'confidence': 0.6}
        ]
        
        result = self.extractor._fuzzy_match_products(products, threshold=0.8)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'Health Tracker')
        self.assertEqual(len(result[0].get('alternative_names', [])), 2)
    
    def test_different_products(self):
        """Test that different products are not merged"""
        products = [
            {'name': 'Health Monitor', 'confidence': 0.8},
            {'name': 'Fitness Tracker', 'confidence': 0.7},
            {'name': 'Medical Assistant', 'confidence': 0.9}
        ]
        
        result = self.extractor._fuzzy_match_products(products)
        self.assertEqual(len(result), 3)


class TestProductClassification(unittest.TestCase):
    """Test product type classification"""
    
    def setUp(self):
        self.extractor = ProductExtractor(use_cache=False)
        self.mock_soup = Mock()
    
    def test_name_based_classification(self):
        """Test classification based on product name"""
        test_cases = [
            ("Health App", "app"),
            ("Monitoring Device", "wearable"),
            ("AI Assistant", "software"),
            ("Therapy Service", "service"),
            ("Analytics Platform", "platform"),
            ("Diagnostic Tool", "tool"),
            ("Sensor Kit", "hardware")
        ]
        
        for name, expected_type in test_cases:
            # Mock the soup find_all to return empty list
            self.mock_soup.find_all.return_value = []
            
            product_type = self.extractor._classify_product(name, self.mock_soup)
            self.assertEqual(product_type, expected_type)
    
    def test_context_based_classification(self):
        """Test classification with context"""
        # Mock context around product mention
        mock_text = Mock()
        mock_text.parent.get_text.return_value = "Download our mobile application from App Store"
        self.mock_soup.find_all.return_value = [mock_text]
        
        product_type = self.extractor._classify_product("HealthTracker", self.mock_soup)
        # Should detect 'app' from context
        self.assertIn(product_type, ['app', 'software'])


class TestGroundTruthMatching(unittest.TestCase):
    """Test ground truth validation"""
    
    def setUp(self):
        self.extractor = ProductExtractor(use_cache=False)
    
    def test_normalized_url_matching(self):
        """Test that ground truth matches with normalized URLs"""
        # Ground truth should be loaded with normalized URLs
        normalized_url = self.extractor.url_normalizer.normalize("https://www.actimi.com/")
        
        gt_products = self.extractor.ground_truth.get(normalized_url, [])
        self.assertGreater(len(gt_products), 0)
        
        # Check specific products
        product_names = [p['name'] for p in gt_products]
        self.assertIn("Actimi Herzinsuffizienz Set", product_names)
        self.assertIn("Actimi Notaufnahme-Set", product_names)
    
    def test_fuzzy_ground_truth_matching(self):
        """Test fuzzy matching for ground truth validation"""
        # This would be tested in the extract_products_from_company method
        # but we can test the logic separately
        from difflib import SequenceMatcher
        
        gt_name = "fyzo Assistant"
        extracted_names = ["fyzo assistant", "Fyzo Assistant", "fyzo-assistant"]
        
        for name in extracted_names:
            similarity = SequenceMatcher(None, gt_name.lower(), name.lower()).ratio()
            self.assertGreaterEqual(similarity, 0.85)


class TestSchemaExtraction(unittest.TestCase):
    """Test schema.org extraction"""
    
    def setUp(self):
        self.extractor = ProductExtractor(use_cache=False)
    
    def test_extended_schema_types(self):
        """Test extraction of extended schema types"""
        test_data = {
            "@type": "MedicalDevice",
            "name": "Heart Monitor Pro"
        }
        
        products = self.extractor._extract_from_schema_data(test_data)
        self.assertIn("Heart Monitor Pro", products)
    
    def test_nested_schema(self):
        """Test nested schema extraction"""
        test_data = {
            "@graph": [
                {
                    "@type": "Organization",
                    "name": "Health Corp"
                },
                {
                    "@type": "SoftwareApplication",
                    "name": "Health Tracker App"
                }
            ]
        }
        
        products = self.extractor._extract_from_schema_data(test_data)
        self.assertIn("Health Tracker App", products)
        self.assertNotIn("Health Corp", products)  # Organization not a product
    
    def test_array_of_types(self):
        """Test products with array of types"""
        test_data = {
            "@type": ["Product", "MedicalDevice"],
            "name": "Smart Thermometer"
        }
        
        products = self.extractor._extract_from_schema_data(test_data)
        self.assertIn("Smart Thermometer", products)


if __name__ == '__main__':
    unittest.main()