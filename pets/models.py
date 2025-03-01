from django.db import models

class User(models.Model):
     username = models.CharField(max_length=150, unique=True,primary_key=True)
     email = models.EmailField(unique=True)
     password = models.CharField(max_length=128)
    
     def __str__(self):
         return f"{self.username}"

class Pet(models.Model):
     
     petname = models.CharField(max_length=100)
     pet_type = models.CharField(max_length=10)
     breed = models.CharField(max_length=100, blank=True, null=True)
     age = models.PositiveIntegerField()
     owner = models.ForeignKey(User,to_field="username", on_delete=models.CASCADE, related_name="pets")

     def __str__(self):
        return f"{self.petname} ({self.pet_type})"
   

 
class ChatHistory(models.Model):
    username = models.CharField(max_length=150)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username}: {self.user_message[:20]}..."
 
        

 