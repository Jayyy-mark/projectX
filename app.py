
from tools.WebSearch import WebSearch
# from tools.imageGenerator import generate_chart
from model.DeepSeek import DeepSeek
from langchain.callbacks.base import BaseCallbackHandler
from langchain.agents import Tool, initialize_agent
from res.memory import load_memory,save_memory
from langchain.memory import ConversationBufferMemory
from flask import Flask, request,render_template, jsonify, send_file
from flask_mysqldb import MySQL
from config import Config
import matplotlib.pyplot as plt
import re
import os
from tools.Mail import send_mail
from pydantic import BaseModel, Field
from flask_cors import CORS
from model.Gemini import GeminiChatbot

#create flask application
app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
STATIC_DIR = 'bot/static/img'

mysql = MySQL(app)


#<============== fucntion for ai tools ===========================>
class SendMailInput(BaseModel):
    receiver_email: str = Field(..., description="Recipient's Gmail address")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")


class ToolUseTracker(BaseCallbackHandler):
    def __init__(self):
        self.tools_used = []

    def on_agent_action(self, action, **kwargs):
        tool_name = action.tool
        if tool_name not in self.tools_used:
            self.tools_used.append(tool_name)
        print(f"Agent used tool: {tool_name}")

# Instantiate tracker
tracker = ToolUseTracker()

# Pass it to your agent when running

# After run, check which tools were used:

tool_used_flag = {"generate_image": False}

def generate_chart(text,filename="chart.png"):
    
    matches = re.findall(r"(\w+)\s+(\d+)", text, re.IGNORECASE)
    labels = [m[0].capitalize() for m in matches]
    values = [int(m[1]) for m in matches]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['green', 'red', 'blue', 'orange'])
    plt.xlabel("Categories")
    plt.ylabel("Values")
    plt.title("Generated Bar Chart")
    plt.tight_layout()
    
    filepath = os.path.join(STATIC_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    tool_used_flag["generate_image"] = True
    return "Successfully created!"



#create LLM
llm = GeminiChatbot()

web = WebSearch()
tool_search = Tool(
        name="Google Search",
        func=web.search,
        description="Search Google using SerpAPI and return multiple results."
    )
tool_generateImage = Tool(
    name="Generate image",
    func=generate_chart,
    description="Generate bar chart,parse the user prompt into like this : (e.g) sale 5000 purchase 10000 expense 20000 income 40000"
)

tool_sendMail = Tool(
    name="Send Mail",
    func=send_mail,
    description=(
        "You can send an email using Gmail SMTP. Extract three parameters from the user request: "
        "1) receiver_email : data type str"
        "2) subject : data type str"
        "3) body : data type str "
        "If any parameter is missing, ask the user for it before calling the tool. "
        "you need to give three parameters to use this tool "
        """(e.g : "receiver_email=aungkyawgun21@gmail.com;subject=meeting;body=come and meet me at 1PM")"""
    ),
)

#get Tools
tools = [tool_search,tool_generateImage,tool_sendMail]



def add_related_suggestions(response, user_message):
    SYSTEM_PROMPT = (
        "You are a helpful assistant. "
        f"Based on the user's question {user_message} and the provided response {response}, answer clearly and concisely. "
        "If the question involves potentially changing information (like people’s roles, dates, laws), "
        "add a polite disclaimer suggesting the user verify with official sources. "
        "Finally, suggest 2-3 relevant follow-up questions or topics the user might want to explore. "
        "Include any source URLs if available."
    )
    user_prompt = (
        f"User question: {user_message}\n"
        f"Current response: {response}\n\n"
        "Please provide an improved answer along with helpful follow-up suggestions."
    )
    suggestion = llm.generate([SYSTEM_PROMPT, user_prompt])
    result = suggestion.generations[0][0].text
    return result


    

#memory file
MEMORY_FILE = "ai_memory.json"

#load past memory
past_memory = load_memory(MEMORY_FILE)
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

for msg in past_memory:
    memory.chat_memory.add_user_message(msg["user"])
    memory.chat_memory.add_ai_message(msg["ai"])


agent = initialize_agent(
    llm=llm,
    tools=tools,
    
    agent="chat-conversational-react-description",
    verbose=True,
    memory=memory,
    max_iterations = 5
)

# ----------------------------
# CHAT LOOP
# ----------------------------


@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/chat", methods=['POST'])
def chat():
    if request.method == 'POST':
        history_data = []

        user_input = request.form['prompt']
        uploaded_file=None
        if "file" in request.files and request.files["file"].filename != "":
        # File exists and is not empty
            uploaded_file = request.files['file']
            response = agent.invoke({"input" : user_input,"file_path":uploaded_file})
            return jsonify({'response' : 'message sent successfully!'})
        else:
            response = agent.invoke({"input" : user_input})
        #response_with_suggestions = add_related_suggestions(response, user_input)
        if tool_used_flag["generate_image"]:
            print("✅ Generate image tool was used")
            tool_used_flag["generate_image"]=False
            image = "static/img/chart.png"
            return jsonify({'response' : response['output'], 'contain_img' : f"http://192.168.142.196:5003/static/img/chart.png"})
        else:
            print("❌ Generate image tool was NOT used")
            return jsonify({'response' : response['output']})

         
    
@app.route('/download')
def download_file():
    image = "static/img/chart.png"
    return send_file(image, mimetype='image/png', as_attachment=True, download_name='chart.png')

@app.route('/test')
def test():
    return jsonify({'message' : 'hello from server'})

app.run(debug=True,host='192.168.142.196',port=5003)



