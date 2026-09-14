"""
webhooks.py - Social Media Webhook Receivers
Receives messages from WhatsApp, Facebook, Twitter, etc.
and uses AI to respond automatically.
"""
from flask import Blueprint, request, jsonify
from models import User, CustomerMessage, db
from ai_engine import ai_assistant

webhooks = Blueprint('webhooks', __name__)


@webhooks.route('/webhook/whatsapp/<int:user_id>', methods=['POST'])
def whatsapp_webhook(user_id):
    data = request.json
    customer_name = data.get('from', 'Unknown')
    message_text = data.get('message', '')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    new_message = CustomerMessage(
        user_id=user_id,
        customer_name=customer_name,
        customer_platform='whatsapp',
        message_text=message_text,
        is_resolved=False
    )
    db.session.add(new_message)
    db.session.commit()
    
    ai_result = ai_assistant.process_customer_message(
        user_id=user_id,
        customer_name=customer_name,
        message=message_text,
        platform='whatsapp'
    )
    
    ai_response = ai_result['response']
    new_message.ai_response = ai_response
    new_message.is_resolved = True
    db.session.commit()
    
    for action in ai_result['actions']:
        _execute_action(action, user_id, customer_name, message_text)
    
    print(f"🤖 AI responded to WhatsApp message from {customer_name}")
    return jsonify({'response': ai_response, 'status': 'sent'})


@webhooks.route('/webhook/facebook/<int:user_id>', methods=['POST'])
def facebook_webhook(user_id):
    data = request.json
    customer_name = data.get('sender_id', 'Unknown')
    message_text = data.get('message', '')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    new_message = CustomerMessage(
        user_id=user_id,
        customer_name=customer_name,
        customer_platform='facebook',
        message_text=message_text,
        is_resolved=False
    )
    db.session.add(new_message)
    db.session.commit()
    
    ai_result = ai_assistant.process_customer_message(
        user_id=user_id,
        customer_name=customer_name,
        message=message_text,
        platform='facebook'
    )
    
    ai_response = ai_result['response']
    new_message.ai_response = ai_response
    new_message.is_resolved = True
    db.session.commit()
    
    for action in ai_result['actions']:
        _execute_action(action, user_id, customer_name, message_text)
    
    print(f"🤖 AI responded to Facebook message from {customer_name}")
    return jsonify({'response': ai_response, 'status': 'sent'})


@webhooks.route('/webhook/instagram/<int:user_id>', methods=['POST'])
def instagram_webhook(user_id):
    data = request.json
    customer_name = data.get('sender_id', 'Unknown')
    message_text = data.get('message', '')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    new_message = CustomerMessage(
        user_id=user_id,
        customer_name=customer_name,
        customer_platform='instagram',
        message_text=message_text,
        is_resolved=False
    )
    db.session.add(new_message)
    db.session.commit()
    
    ai_result = ai_assistant.process_customer_message(
        user_id=user_id,
        customer_name=customer_name,
        message=message_text,
        platform='instagram'
    )
    
    ai_response = ai_result['response']
    new_message.ai_response = ai_response
    new_message.is_resolved = True
    db.session.commit()
    
    for action in ai_result['actions']:
        _execute_action(action, user_id, customer_name, message_text)
    
    print(f"🤖 AI responded to Instagram message from {customer_name}")
    return jsonify({'response': ai_response, 'status': 'sent'})


def _execute_action(action, user_id, customer_name, message_text):
    action_type = action['type']
    try:
        if action_type == 'create_order':
            product_name = None
            for word in message_text.split():
                if word.lower() not in ['i', 'want', 'to', 'order', 'buy', 'the', 'a', 'an']:
                    product_name = word
                    break
            
            order = ai_assistant.create_order_from_conversation(
                user_id=user_id,
                customer_name=customer_name,
                product_name=product_name
            )
            print(f"📦 Created order #{order.id} for {customer_name}")
        
        elif action_type == 'schedule_meeting':
            meeting = ai_assistant.schedule_meeting_from_conversation(
                user_id=user_id,
                customer_name=customer_name,
                meeting_title='Customer Inquiry'
            )
            print(f"📅 Scheduled meeting #{meeting.id} with {customer_name}")
        
        elif action_type == 'collect_lead':
            lead = ai_assistant.collect_lead_from_conversation(
                user_id=user_id,
                customer_name=customer_name,
                platform='whatsapp'
            )
            print(f"🎯 Collected lead for {customer_name}")
    except Exception as e:
        print(f"❌ Error executing action {action_type}: {e}")


@webhooks.route('/test-ai/<int:user_id>', methods=['POST'])
def test_ai(user_id):
    data = request.json
    customer_name = data.get('customer_name', 'Test Customer')
    message = data.get('message', '')
    platform = data.get('platform', 'whatsapp')
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    result = ai_assistant.process_customer_message(
        user_id=user_id,
        customer_name=customer_name,
        message=message,
        platform=platform
    )
    
    # FIXED: Removed 'customer_id' from here
    new_message = CustomerMessage(
        user_id=user_id,
        customer_name=customer_name,
        customer_platform=platform,
        message_text=message,
        ai_response=result['response'],
        is_resolved=True
    )
    db.session.add(new_message)
    db.session.commit()
    
    for action in result['actions']:
        _execute_action(action, user_id, customer_name, message)
    
    return jsonify({
        'ai_response': result['response'],
        'actions_taken': result['actions'],
        'message_saved': True
    })