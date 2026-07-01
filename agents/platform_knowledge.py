import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

load_dotenv()

# We can reuse llama-3.1-8b-instant for fast matching and translation
_llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY"),
)

PLATFORM_FAQ_ITEMS = [
    {
        "id": 1,
        "question": "إزاي أبدأ أستخدم المنصة؟",
        "answer": (
            "لبدء استخدام Rental Hub، لازم أولاً إنشاء حساب وتسجيل الدخول. بعد كده تقدر تختار نوع الاستخدام: إما مستأجر أو مالك منتجات. \n"
            "لو مستأجر، تقدر تتصفح المنتجات وتختار المنتج المناسب، لكن لازم يكون عندك رصيد كافي أو وسيلة دفع مفعلة علشان تقدر تأكد طلب التأجير وتكمل العملية. \n"
            "لو مالك منتجات، لازم تشترك في باقة وتقوم بشحن رصيد داخل المنصة، وده بيتم استخدامه في تفعيل حسابك وإتاحة إضافة المنتجات وإدارتها. \n"
            "بعد الاشتراك، تقدر تضيف منتجاتك بسهولة مع الصور والوصف والسعر ومدة التأجير، وبعد المراجعة بتكون متاحة للمستخدمين."
        )
    },
    {
        "id": 2,
        "question": "إيه هي Rental Hub؟",
        "answer": (
            "Rental Hub هي منصة ذكية بتربط بين أصحاب المنتجات والأشخاص اللي محتاجين يستأجروها، وبتسهل عملية التأجير بشكل آمن ومنظم بدل الشراء التقليدي، بحيث تقدر تستفيد من المنتجات بشكل مؤقت وبأقل تكلفة."
        )
    },
    {
        "id": 3,
        "question": "إيه الهدف من المنصة؟",
        "answer": (
            "هدف Rental Hub هو تسهيل عملية تأجير واستئجار المنتجات بين المستخدمين بطريقة آمنة وموثوقة، مع تقليل التكاليف على المستأجرين، ومساعدة أصحاب المنتجات إنهم يحققوا دخل من ممتلكاتهم."
        )
    },
    {
        "id": 4,
        "question": "هل أقدر أعرض منتجاتي للتأجير؟",
        "answer": (
            "نعم، تقدر تعرض منتجاتك بسهولة على المنصة بعد الاشتراك في الباقة المناسبة. كل اللي عليك تضيف بيانات المنتج زي الصور والوصف والسعر ومدة التأجير، وبعد مراجعة بسيطة بيتم نشره على المنصة ليكون متاح للمستخدمين."
        )
    },
    {
        "id": 5,
        "question": "إزاي المنصة بتحافظ على حقوق المؤجر والمستأجر؟",
        "answer": (
            "المنصة بتوفر نظام حماية للطرفين، حيث يتم أخذ تأمين (Deposit) من المستأجر قبل استلام المنتج كضمان ضد أي تلفيات أو سوء استخدام. في حالة وجود مشكلة، يقدر المؤجر او المالك يقدم بلاغ، ويتم مراجعته من فريق المنصة واتخاذ الإجراء المناسب سواء تعويض أو خصم من التأمين لضمان حقوق الطرفين."
        )
    },
    {
        "id": 6,
        "question": "ازاي ممكن اجر علي المنصه",
        "answer": (
            "تقدر تبدأ التأجير من خلال البحث عن المنتج المناسب، ثم الدخول على صفحة التفاصيل وتقديم طلب تأجير. بعد موافقة صاحب المنتج، يتم تأكيد الطلب واستكمال عملية التأجير بكل سهولة."
        )
    },
    {
        "id": 7,
        "question": "إزاي أقدر أسحب فلوسي من المنصة؟",
        "answer": (
            "تقدر تسحب أرباحك عن طريق تقديم طلب سحب من حسابك داخل المنصة. بتحدد المبلغ المطلوب وسيلة التحويل المناسبة ليك (مثل انستاباي، فودافون كاش، أو بطاقة بنكية)، وبعدها بيتم مراجعة الطلب من إدارة المنصة، وفي حالة الموافقة بيتم تحويل الأموال لك بالطريقة التي اخترتها."
        )
    },
    {
        "id": 8,
        "question": "إيه هي طرق السحب والإيداع (شحن الرصيد) المتاحة؟",
        "answer": (
            "تقدر تسحب أرباحك أو تودع (تشحن) رصيدك في المنصة بكل سهولة عن طريق واحدة من الطرق دي: انستاباي (InstaPay)، أو فودافون كاش، أو باستخدام بطاقة بنكية."
        )
    }
]

# Prompt to match query to the most appropriate FAQ key using ID
_match_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an assistant that matches a user query to one of the predefined FAQ questions.\n"
        "Here are the predefined questions with their numeric IDs:\n"
        "{faq_list}\n\n"
        "Return a JSON object containing:\n"
        "- 'matched_id': the integer ID of the matched question from the list above, or null if no question is a close match.\n"
        "- 'confidence': a float between 0.0 and 1.0 representing how confident you are.\n"
        "Format the output strictly as JSON, e.g.:\n"
        '{{"matched_id": 2, "confidence": 0.95}}'
    )),
    ("human", "User query: {user_query}")
])

_match_chain = _match_prompt | _llm | JsonOutputParser()

# Prompt to translate Arabic response into English
_translate_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a professional translator. Translate the following Arabic text about a rental platform into clear, natural, and friendly English.\n"
        "Keep the exact same meaning and friendly tone. Do not add any extra info."
    )),
    ("human", "{text}")
])

_translate_chain = _translate_prompt | _llm | StrOutputParser()

def _is_arabic(text: str) -> bool:
    if not text:
        return False
    return any('\u0600' <= c <= '\u06FF' for c in text)

def answer_platform_question(query: str, chat_history: list = None) -> str:
    """
    Matches the user query with the platform FAQ database.
    If match is successful, returns the approved answer.
    If the query is in English (detected via characters), translates the answer to English.
    """
    faq_list_str = "\n".join([f"{item['id']}. {item['question']}" for item in PLATFORM_FAQ_ITEMS])
    try:
        match_res = _match_chain.invoke({
            "faq_list": faq_list_str,
            "user_query": query
        })
        matched_id = match_res.get("matched_id")
        confidence = match_res.get("confidence", 0.0)
    except Exception as e:
        print(f"[PlatformKnowledge] Matching Error: {e}")
        matched_id = None
        confidence = 0.0

    # Find the matched item by ID
    matched_item = None
    if matched_id is not None:
        for item in PLATFORM_FAQ_ITEMS:
            if item["id"] == int(matched_id):
                matched_item = item
                break

    # If confidence is too low or not matched, use default fallback
    if not matched_item or confidence < 0.6:
        if _is_arabic(query):
            return "للأسف، مش لاقي إجابة محددة لسؤالك بخصوص المنصة حالياً. تقدر تتواصل مع خدمة العملاء أو الدعم الفني لمساعدتك."
        else:
            return "Unfortunately, I couldn't find a specific answer to your question about the platform. Please feel free to contact our support team for assistance."

    answer = matched_item["answer"]

    # Check if the query is English (non-Arabic) to translate the answer
    if not _is_arabic(query):
        try:
            translated_answer = _translate_chain.invoke({"text": answer})
            return translated_answer.strip()
        except Exception as e:
            print(f"[PlatformKnowledge] Translation Error: {e}")
            # Fallback to Arabic answer if translation fails
            return answer

    return answer
