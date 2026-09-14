"""
ai_engine.py - The AI Brain
This handles all intelligent customer interactions.
"""
import openai
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from models import db, Product, Order, Lead, Meeting


class AIAssistant:
    """The AI assistant that handles customer interactions"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("❌ OPENAI_API_KEY not found in .env file! Please check your .env file.")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def process_customer_message(self, user_id, customer_name, message, platform='whatsapp'):
        """Process a customer message and generate an intelligent response."""
        products = Product.query.filter_by(user_id=user_id, is_available=True).all()
        context = self._build_context(user_id, products, customer_name)
        response = self._generate_response(context, message)
        actions = self._extract_actions(response, user_id, customer_name, platform)
        
        return {
            'response': response,
            'actions': actions
        }
    
    def _build_context(self, user_id, products, customer_name):
        """Build the context for the AI"""
        product_list = "\n".join([
            f"- {p.name}: ${p.price} (Stock: {p.stock}) - {p.description or 'No description'}"
            for p in products
        ])
        
        return f"""You are a helpful AI assistant for a business. You are chatting with a customer named {customer_name}.

AVAILABLE PRODUCTS:
{product_list if product_list else 'No products available right now.'}

YOUR CAPABILITIES:
1. Answer questions about products, prices, and stock
2. Take orders and provide delivery dates (typically 3-7 business days)
3. Schedule meetings with the business owner
4. Collect customer information (name, email, phone, best time to contact)

INSTRUCTIONS:
- Be friendly, professional, and helpful
- If they ask about a product, provide the price and stock
- If they want to order, collect their details and confirm the order
- If they want a meeting, ask for their preferred date/time
- Keep responses concise but informative (under 100 words if possible)
- Use emojis occasionally to be friendly

RESPONSE FORMAT:
Respond naturally as a helpful assistant."""
    
    def _generate_response(self, context, message):
        """Generate AI response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return "I'm sorry, I'm having trouble connecting right now. Please try again in a moment!"
    
    def _extract_actions(self, response, user_id, customer_name, platform):
        """Extract any actions that need to be taken from the AI response"""
        actions = []
        response_lower = response.lower()
        
        if any(word in response_lower for word in ['order', 'buy', 'purchase', 'want to get', 'i will take']):
            actions.append({'type': 'create_order', 'data': {'customer_name': customer_name, 'platform': platform}})
        
        if any(word in response_lower for word in ['meeting', 'appointment', 'schedule', 'call', 'discuss']):
            actions.append({'type': 'schedule_meeting', 'data': {'customer_name': customer_name, 'platform': platform}})
        
        if any(word in response_lower for word in ['contact', 'reach you', 'email', 'phone', 'number']):
            actions.append({'type': 'collect_lead', 'data': {'customer_name': customer_name, 'platform': platform}})
        
        return actions

    def create_order_from_conversation(self, user_id, customer_name, product_name=None, quantity=1, platform='web'):
        """Create an order based on the conversation"""
        product = None
        if product_name:
            product = Product.query.filter_by(user_id=user_id, name=product_name).first()
        
        delivery_date = datetime.utcnow() + timedelta(days=7)
        
        order = Order(
            user_id=user_id,
            customer_name=customer_name,
            product_id=product.id if product else None,
            quantity=quantity,
            total_price=float(product.price * quantity) if product else 0.0,
            delivery_date=delivery_date,
            status='pending',
            notes=f'Order created via AI assistant on {platform}'
        )
        db.session.add(order)
        db.session.commit()
        return order
    
    def collect_lead_from_conversation(self, user_id, customer_name, email=None, phone=None, interest=None, platform='whatsapp'):
        """Collect a lead from the conversation"""
        lead = Lead(
            user_id=user_id,
            name=customer_name,
            email=email,
            phone=phone,
            source=platform,
            interest=interest,
            status='new'
        )
        db.session.add(lead)
        db.session.commit()
        return lead
    
    def schedule_meeting_from_conversation(self, user_id, customer_name, meeting_title, meeting_date=None):
        """Schedule a meeting based on the conversation"""
        if not meeting_date:
            meeting_date = datetime.utcnow() + timedelta(days=3)
        
        meeting = Meeting(
            user_id=user_id,
            title=f'Meeting with {customer_name}: {meeting_title}',
            meeting_date=meeting_date,
            duration_minutes=30,
            status='scheduled',
            description=f'Meeting scheduled via AI assistant with {customer_name}'
        )
        db.session.add(meeting)
        db.session.commit()
        return meeting


# Create a global instance
ai_assistant = AIAssistant()