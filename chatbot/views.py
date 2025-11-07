from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
from django.db.models import Q
import json
import uuid
import re
from datetime import datetime, timedelta

from .models import ChatSession, ChatMessage, FAQ
from products.models import Product
from categories.models import Category
from artists.models import Artist

# Create your views here.

class ChatbotView(View):
    """Main chatbot view"""
    
    def get(self, request):
        """Render the chatbot interface"""
        return render(request, 'chatbot/chatbot.html')
    
    def post(self, request):
        """Handle chat messages"""
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Get or create chat session
            if session_id:
                try:
                    session = ChatSession.objects.get(session_id=session_id)
                except ChatSession.DoesNotExist:
                    session = None
            else:
                session = None
            
            if not session:
                session = ChatSession.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    session_id=str(uuid.uuid4())
                )
            
            # Save user message
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=message
            )
            
            # Generate bot response
            bot_response = self.generate_response(message, request.user)
            
            # Save bot response
            bot_message = ChatMessage.objects.create(
                session=session,
                message_type='bot',
                content=bot_response
            )
            
            return JsonResponse({
                'response': bot_response,
                'session_id': session.session_id,
                'timestamp': bot_message.timestamp.isoformat()
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)
    
    def generate_response(self, message, user):
        """Generate bot response based on user message"""
        message_lower = message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']):
            return self.get_greeting_response(user)
        
        # Help responses
        if any(word in message_lower for word in ['help', 'what can you do', 'commands', 'options']):
            return self.get_help_response()
        
        # Artist contact specific
        if any(phrase in message_lower for phrase in ['contact artist', 'contact artists', 'how to contact artist', 'reach artist', 'message artist']):
            return self.get_artist_contact_response()
        
        # Artist information (general)
        if any(word in message_lower for word in ['artist', 'creator', 'maker', 'who made']) and not any(word in message_lower for word in ['contact', 'reach', 'message']):
            return self.search_artists(message)
        
        # Product search
        if any(word in message_lower for word in ['product', 'item', 'buy', 'purchase', 'shop', 'store', 'show me', 'find']):
            return self.search_products(message)
        
        # Category information
        if any(word in message_lower for word in ['category', 'type', 'kind', 'style', 'categories']):
            return self.search_categories(message)
        
        # Order information
        if any(word in message_lower for word in ['order', 'track', 'delivery', 'shipping', 'status']):
            return self.get_order_info_response()
        
        # Contact information (general)
        if any(word in message_lower for word in ['contact', 'email', 'phone', 'address', 'location']) and not any(word in message_lower for word in ['artist']):
            return self.get_contact_response()
        
        # FAQ matching
        faq_response = self.search_faq(message)
        if faq_response:
            return faq_response
        
        # Default response
        return self.get_default_response()
    
    def get_greeting_response(self, user):
        """Generate greeting response"""
        if user and user.is_authenticated:
            return f"Hello {user.first_name or user.username}! 👋 Welcome to Crafty! I'm here to help you with any questions about our handmade crafts, artists, or orders. What would you like to know?"
        else:
            return "Hello! 👋 Welcome to Crafty! I'm your friendly assistant here to help you discover amazing handmade crafts from talented artists. What can I help you with today?"
    
    def get_help_response(self):
        """Generate help response"""
        return """I can help you with many things! Here's what I can do:

🛍️ **Product Information**: Ask about specific products, prices, or availability
👨‍🎨 **Artist Details**: Learn about our talented craft artists
📂 **Categories**: Browse different craft categories like jewelry, home decor, etc.
📦 **Orders**: Get help with order tracking, delivery, or returns
❓ **General Questions**: Ask about our policies, shipping, or anything else

Just type your question naturally, and I'll do my best to help! For example:
- "Show me jewelry products"
- "Who are your artists?"
- "How do I track my order?"
- "What's your return policy?"

What would you like to know?"""
    
    def search_products(self, message):
        """Search for products based on message"""
        # Extract keywords from message
        keywords = re.findall(r'\b\w+\b', message.lower())
        
        # Search products
        products = Product.objects.filter(
            Q(name__icontains=message) |
            Q(description__icontains=message) |
            Q(craft_category__icontains=message),
            available=True
        )[:5]
        
        if products:
            response = "I found some products that might interest you:\n\n"
            for product in products:
                price = product.discount_price if product.discount_price else product.price
                response += f"🛍️ **{product.name}** - {price} DZD\n"
                response += f"   By {product.artist.name}\n"
                response += f"   {product.description[:100]}...\n\n"
            response += "Would you like to know more about any specific product?"
        else:
            response = "I couldn't find specific products matching your request. Here are some popular categories:\n\n"
            categories = Product.CRAFT_CHOICES[:5]
            for code, name in categories:
                response += f"• {name}\n"
            response += "\nTry asking about a specific category or product name!"
        
        return response
    
    def search_artists(self, message):
        """Search for artists based on message"""
        artists = Artist.objects.filter(
            Q(name__icontains=message) |
            Q(bio__icontains=message),
            featured=True
        )[:5]
        
        if artists:
            response = "Here are some of our talented artists:\n\n"
            for artist in artists:
                response += f"👨‍🎨 **{artist.name}**\n"
                if artist.bio:
                    response += f"   {artist.bio[:100]}...\n"
                response += f"   Available for commissions: {'Yes' if artist.availability else 'No'}\n\n"
        else:
            response = "We have many talented artists creating beautiful handmade crafts! You can browse all artists on our website or ask about specific craft types."
        
        return response
    
    def search_categories(self, message):
        """Search for categories based on message"""
        categories = Product.CRAFT_CHOICES
        response = "Here are our craft categories:\n\n"
        
        for code, name in categories:
            response += f"• **{name}**\n"
        
        response += "\nYou can ask me about products in any of these categories!"
        return response
    
    def get_order_info_response(self):
        """Generate order information response"""
        return """📦 **Order Information**

Here's what I can help you with regarding orders:

• **Track your order**: Log in to your account to see order status
• **Delivery time**: Usually 3-7 business days within Algeria
• **Shipping cost**: Calculated at checkout based on your location
• **Returns**: 7-day return policy for unused items
• **Contact support**: Email us at support@crafty.com

If you have a specific order question, please log in to your account or contact our support team with your order number."""

    def get_artist_contact_response(self):
        """Generate artist contact information response"""
        return """👨‍🎨 **Contacting Artists**

Here's how you can reach our talented artists:

**Direct Contact:**
• Visit any artist's profile page on our website
• Click the "Contact Artist" button on their profile
• Send them a direct message through our platform

**Artist Profiles Include:**
• Contact information (email, phone if provided)
• Social media links
• Portfolio and previous work
• Availability for custom orders

**Custom Orders:**
• Many artists accept custom commissions
• Contact them directly to discuss your ideas
• They can provide quotes and timelines

**Browse Artists:**
• Go to "Artisans" in our main menu
• Filter by craft type or location
• View their profiles and contact information

Would you like me to help you find artists in a specific category?"""

    def get_contact_response(self):
        """Generate contact information response"""
        return """📞 **Contact Information**

You can reach us through:

📧 **Email**: support@crafty.com
📱 **Phone**: +213 XXX XXX XXX
📍 **Address**: [Your Address Here]
🕒 **Hours**: Monday-Friday, 9 AM - 6 PM

For order inquiries, please include your order number. For general questions, feel free to ask me anything!"""

    def search_faq(self, message):
        """Search FAQ for matching questions"""
        keywords = re.findall(r'\b\w+\b', message.lower())
        
        # Search FAQs
        faqs = FAQ.objects.filter(is_active=True)
        best_match = None
        max_matches = 0
        
        for faq in faqs:
            faq_keywords = faq.get_keywords_list()
            matches = sum(1 for keyword in keywords if keyword in faq_keywords)
            if matches > max_matches:
                max_matches = matches
                best_match = faq
        
        if best_match and max_matches > 0:
            return f"**Q: {best_match.question}**\n\nA: {best_match.answer}"
        
        return None
    
    def get_default_response(self):
        """Generate default response when no specific match is found"""
        responses = [
            "I'm not sure I understand that question. Could you rephrase it or ask about our products, artists, or orders?",
            "That's an interesting question! I'm still learning. Try asking about our handmade crafts, artists, or how to place an order.",
            "I'd be happy to help! You can ask me about our products, artists, categories, or order information. What would you like to know?",
            "Let me help you with that! Try asking about specific products, our artists, or order-related questions."
        ]
        
        import random
        return random.choice(responses)

@require_http_methods(["GET"])
def get_chat_history(request, session_id):
    """Get chat history for a session"""
    try:
        session = ChatSession.objects.get(session_id=session_id)
        messages = session.messages.all()[:50]  # Last 50 messages
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'type': message.message_type,
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
            })
        
        return JsonResponse({
            'messages': messages_data,
            'session_id': session_id
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)

@require_http_methods(["POST"])
def clear_chat_history(request):
    """Clear chat history for a session"""
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id', '')
        
        if session_id:
            session = ChatSession.objects.get(session_id=session_id)
            session.messages.all().delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Session ID required'}, status=400)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)