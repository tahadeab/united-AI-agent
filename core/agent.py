import os
from openai import OpenAI
from .memory import Memory

class UnitedAgent:
    def __init__(self, model="gpt-4.1-mini"):
        self.client = OpenAI()
        self.memory = Memory()
        self.model = model
        self.system_prompt = (
            "أنت 'يونايتد' (United)، عميل ذكي متطور ومتعدد المهام. "
            "تتميز بالذكاء، السرعة، والقدرة على مساعدة المستخدم في مختلف المجالات. "
            "تحدث دائماً باللغة العربية بأسلوب مهني وودود."
        )

    def chat(self, user_input):
        # إضافة رسالة المستخدم للذاكرة
        self.memory.add_message("user", user_input)
        
        # تحضير الرسائل مع الـ System Prompt
        messages = [{"role": "system", "content": self.system_prompt}] + self.memory.get_history()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            ai_message = response.choices[0].message.content
            # إضافة رد العميل للذاكرة
            self.memory.add_message("assistant", ai_message)
            return ai_message
            
        except Exception as e:
            return f"عذراً، حدث خطأ أثناء معالجة طلبك: {str(e)}"
