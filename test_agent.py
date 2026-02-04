from core.agent import UnitedAgent

def test_united_agent():
    print("بدء اختبار العميل يونايتد...")
    agent = UnitedAgent()
    
    # اختبار التحية والتعريف بالنفس
    print("\nالاختبار 1: التحية")
    response = agent.chat("مرحباً، من أنت؟")
    print(f"الرد: {response}")
    
    # اختبار الذاكرة
    print("\nالاختبار 2: الذاكرة (تذكر الاسم)")
    agent.chat("اسمي أحمد، تذكر ذلك.")
    response = agent.chat("ما هو اسمي؟")
    print(f"الرد: {response}")
    
    if "أحمد" in response:
        print("\nنتيجة الاختبار: نجاح! العميل يعمل ويتذكر السياق.")
    else:
        print("\nنتيجة الاختبار: فشل في تذكر الاسم.")

if __name__ == "__main__":
    test_united_agent()
