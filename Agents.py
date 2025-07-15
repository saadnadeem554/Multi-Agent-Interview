from crewai import Agent, Task, Crew
from crewai_tools import ( ScrapeWebsiteTool, GithubSearchTool )
import os
from utils import get_openai_api_key

openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

recruiter_text = " add some details about the recruiter here. "
resumetext = """ Extract text from resume and add here. """

github_tool = GithubSearchTool(
    gh_token="Add your github token here", 
    content_types=["repositories", "code"]
)

# Define agents and tasks for the recruitment interview process
research_agent = Agent(
    role="Research Analyst of recruiters",
    goal="Given a profile extract information about the recruiter and create a detailed charachter profile",
    backstory="You are an experienced recruiter researcher with strong skills in analyzing recruiters and understanding their thought processes.",
    verbose=True,  # Enable logging for debugging
    allow_delegation=False
)
research_task = Task(
    description="""
        You are given a short profile of a recruiter. Your task is to get the most relevant information about the recruiter and create a detailed character profile based on their skills, experience, and projects and personal interests. 
        {profile} is the url of the linkedin profile of the recruiter.
    """,
    expected_output="""
       a detailed character profile of the recruiter, focusing on their personality and how they would likely approach candidate selection and evaluation.
    """,
    agent=research_agent
    
)
candidate_research_agent = Agent(
    role="Research Analyst of candidates",
    goal="Given a github profile and a candidate's resume extract information about the candidate and create a detailed charachter profile based on their skills, experience, and projects.",
    backstory="You are an experienced candidate researcher with strong skills in analyzing candidates and understanding their skills and expertise.",
    tools=[github_tool, ScrapeWebsiteTool()],
    verbose=True,  # Enable logging for debugging
    allow_delegation=False
)
candidate_research_task = Task(
    description="""You are given a github profile of a candidate as well as their resume. Your task is to get the most relevant information about the candidate and create a detailed character profile based on their skills, experience, and projects. Your output will be given to another agent who will use this information to act as the candidate in a mock interview.
        {profile_url} is the url of the github profile of the candidate.
        resume: {resume}
    """,
    expected_output="""
       a detailed character profile of the candidate, focusing on their skills, experience, and projects.
    """,
    agent=candidate_research_agent
)
interview_agent = Agent(
    role="Mock Interviewer",
    goal="Create a set of detailed and challenging interview questions based on the provided job description and the recruiter's character profile.",
    backstory="You are an experienced recruiter based on the provided profile with strong skills in evaluating candidates according to the job description and candidates resume.",
    verbose=True,  # Enable logging for debugging
    allow_delegation=False
)
interview_task = Task(
    description="""You are given a detailed character profile of a recruiter that you have to imitate. Your task is to generate a set of Interview questions related to the job description and resume of the candidate.
    job description: {job_description}
    candidate profile: {resume}
    """,
    expected_output="""
    A list of at least 10 well-structured and challenging interview questions tailored to the candidate's resume and the job description.
    These questions should reflect the recruiter's background and focus areas.
    """,
    agent=interview_agent,
    context=[research_task, candidate_research_task] 
)
candidate_answer_agent = Agent(
    role="Mock Candidate",
    goal="Answer the interview questions based on the candidate's character profile and resume.",
    backstory="You are an experienced candidate based on the provided profile with strong skills in answering interview questions according to the job description and your resume.",
    verbose=True,  # Enable logging for debugging
    allow_delegation=False
)
candidate_answer_task = Task(
    description="""You are given a detailed character profile of a candidate that you have to imitate. Your task is to answer the interview questions based on the candidate's character profile and resume.
    candidate profile: {resume}
    """,
    expected_output="""
    A set of well-structured and thoughtful answers to the interview questions based on the candidate's profile and resume.
    """,
    agent=candidate_answer_agent,
    context=[interview_task, candidate_research_task]
    
)
input_data = {
    "profile": recruiter_text,
    "resume": resumetext,
    "profile_url": "add the github profile url of the candidate here",  # Add candidate's GitHub profile URL
    "job_description": "Add Job Description Here"  # Add job description
}

crew = Crew(
    agents=[research_agent, candidate_research_agent, interview_agent, candidate_answer_agent],
    tasks=[research_task, candidate_research_task, interview_task, candidate_answer_task],
)

result = crew.kickoff(
    inputs=input_data
)

print(result)