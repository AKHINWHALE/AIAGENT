"""
approval.py - Manages the approval workflow
Posts must be approved via WhatsApp before being published
"""
import json
import os
from datetime import datetime
from whatsapp import whatsapp


class ApprovalManager:
    """
    This class manages the approval workflow for social media posts.
    It tracks pending, approved, and rejected posts.
    """
    
    def __init__(self):
        """
        Initialize the Approval Manager.
        Sets up file paths for tracking posts.
        """
        # File to store posts waiting for approval
        self.pending_file = "pending_posts.json"
        
        # File to store approved posts
        self.approved_file = "approved_posts.json"
        
        # File to store rejected posts
        self.rejected_file = "rejected_posts.json"
    
    def get_pending_posts(self):
        """
        Get all posts waiting for approval.
        
        Returns:
            A list of post dictionaries
        """
        # Check if the pending file exists
        if not os.path.exists(self.pending_file):
            return []
        
        # Open and read the file
        with open(self.pending_file, "r") as f:
            lines = f.readlines()
        
        # Parse each line as JSON
        posts = []
        for line in lines:
            try:
                posts.append(json.loads(line.strip()))
            except:
                # Skip invalid lines
                continue
        
        return posts
    
    def send_all_pending_for_approval(self):
        """
        Send all pending posts to WhatsApp for approval.
        """
        # Get all pending posts
        posts = self.get_pending_posts()
        
        # If no posts, print a message
        if not posts:
            print("No pending posts to approve")
            return
        
        # Loop through each post
        for i, post in enumerate(posts):
            # Generate a unique post ID
            post_id = f"POST_{i}_{int(datetime.now().timestamp())}"
            post["id"] = post_id
            
            # Send the approval request via WhatsApp
            whatsapp.send_approval_request(
                platform=post.get("platform", "unknown"),
                content=post.get("content", ""),
                post_id=post_id
            )
        
        print(f"✅ Sent {len(posts)} posts for approval")
    
    def process_approval(self, post_id: str, decision: str, new_content: str = None):
        """
        Process an approval decision from WhatsApp.
        
        Args:
            post_id: The ID of the post
            decision: "approved" or "rejected"
            new_content: Optional new content if editing
        
        Returns:
            True if processed successfully, False otherwise
        """
        # Get all pending posts
        posts = self.get_pending_posts()
        
        # Find the target post and separate it from the rest
        target_post = None
        remaining_posts = []
        
        for post in posts:
            if post.get("id") == post_id:
                target_post = post
            else:
                remaining_posts.append(post)
        
        # If post not found, return False
        if not target_post:
            print(f"Post {post_id} not found")
            return False
        
        # Add decision metadata
        target_post["decision"] = decision
        target_post["decided_at"] = datetime.now().isoformat()
        
        # If new content provided, update it
        if new_content:
            target_post["content"] = new_content
        
        # Save the decision
        if decision == "approved":
            # Append to approved file
            with open(self.approved_file, "a") as f:
                f.write(json.dumps(target_post) + "\n")
            
            # TODO: Actually post to social media here
            print(f"✅ Post {post_id} approved - ready to publish")
        
        else:
            # Append to rejected file
            with open(self.rejected_file, "a") as f:
                f.write(json.dumps(target_post) + "\n")
            
            print(f"❌ Post {post_id} rejected")
        
        # Update the pending file (remove the processed post)
        with open(self.pending_file, "w") as f:
            for post in remaining_posts:
                f.write(json.dumps(post) + "\n")
        
        return True


# ============================================================
# THIS IS THE LINE THAT WAS MISSING!
# ============================================================
# Create a global Approval Manager instance
approval_manager = ApprovalManager()