from django.core.management.base import BaseCommand
from chatbot.models import FAQ

class Command(BaseCommand):
    help = 'Load sample FAQ data for the chatbot'

    def handle(self, *args, **options):
        sample_faqs = [
            {
                'question': 'What is your return policy?',
                'answer': 'We offer a 7-day return policy for unused items in original condition. Items must be returned with original packaging and tags. Custom or personalized items cannot be returned unless there is a defect.',
                'keywords': 'return, refund, policy, exchange, send back',
                'category': 'Returns'
            },
            {
                'question': 'How long does shipping take?',
                'answer': 'Standard shipping within Algeria takes 3-7 business days. Express shipping (1-3 days) is available for an additional fee. International shipping times vary by destination.',
                'keywords': 'shipping, delivery, time, how long, when, arrive',
                'category': 'Shipping'
            },
            {
                'question': 'Do you offer custom orders?',
                'answer': 'Yes! Many of our artists accept custom orders. You can contact them directly through their profile pages or use our custom order form. Custom items may take 2-4 weeks to complete.',
                'keywords': 'custom, personalized, made to order, special request, bespoke',
                'category': 'Custom Orders'
            },
            {
                'question': 'How do I track my order?',
                'answer': 'Once your order ships, you will receive a tracking number via email. You can also log into your account and check the order status in your dashboard.',
                'keywords': 'track, tracking, order status, where is my order, delivery',
                'category': 'Orders'
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': 'We accept all major credit cards (Visa, Mastercard), PayPal, and bank transfers. Payment is processed securely through our encrypted payment gateway.',
                'keywords': 'payment, pay, credit card, visa, mastercard, paypal, how to pay',
                'category': 'Payment'
            },
            {
                'question': 'Are your products handmade?',
                'answer': 'Yes! All products on Crafty are handmade by talented local artists. Each piece is unique and crafted with care and attention to detail.',
                'keywords': 'handmade, handcrafted, artisan, local, unique, authentic',
                'category': 'Products'
            },
            {
                'question': 'How do I become an artist on Crafty?',
                'answer': 'To become an artist, create an account and select "Artist" as your role. Complete your artist profile with photos of your work, bio, and contact information. Our team will review your application.',
                'keywords': 'become artist, sell, join, apply, artist application, how to sell',
                'category': 'Artists'
            },
            {
                'question': 'Do you ship internationally?',
                'answer': 'Currently, we primarily serve customers in Algeria. International shipping may be available for select items. Please contact us for international shipping options and rates.',
                'keywords': 'international, worldwide, outside algeria, abroad, export',
                'category': 'Shipping'
            },
            {
                'question': 'What if my item arrives damaged?',
                'answer': 'If your item arrives damaged, please contact us within 48 hours with photos of the damage. We will arrange for a replacement or full refund, including return shipping costs.',
                'keywords': 'damaged, broken, defect, problem, issue, not working',
                'category': 'Returns'
            },
            {
                'question': 'How do I contact customer support?',
                'answer': 'You can reach our customer support team via email at support@crafty.com, phone at +213 XXX XXX XXX, or through the contact form on our website. We typically respond within 24 hours.',
                'keywords': 'contact, support, help, email, phone, customer service',
                'category': 'Contact'
            }
        ]

        created_count = 0
        for faq_data in sample_faqs:
            faq, created = FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults={
                    'answer': faq_data['answer'],
                    'keywords': faq_data['keywords'],
                    'category': faq_data['category'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created FAQ: {faq.question}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'FAQ already exists: {faq.question}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully loaded {created_count} sample FAQs')
        )
