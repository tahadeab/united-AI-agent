import sys
from core.agent import UnitedAgent

def main():
    agent = UnitedAgent()
    print("مرحباً! أنا 'يونايتد'، عميلك الذكي. كيف يمكنني مساعدتك اليوم؟ (اكتب 'خروج' للإنهاء)")
    
    while True:
        try:
            user_input = input("أنت: ")
            if user_input.lower() in ['خروج', 'exit', 'quit']:
                print("يونايتد: وداعاً! أتطلع لمساعدتك مرة أخرى.")
                break
            
            if not user_input.strip():
                continue
                
            response = agent.chat(user_input)
            print(f"يونايتد: {response}")
            
        except KeyboardInterrupt:
            print("\nيونايتد: تم إنهاء الجلسة. وداعاً!")
            break
        except Exception as e:
            print(f"يونايتد: حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    main()
