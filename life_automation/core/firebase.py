import firebase_admin
from firebase_admin import auth, credentials, firestore

cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
auth = auth

USERS_COLLECTION = db.collection("users")
EMAIL_JOBS_COLLECTION = db.collection("jobs")
PUBLISHING_JOBS_COLLECTION = db.collection("publishing_jobs")


def setup_sample_db():
    with open("life_automation/templates/sample_email.txt") as f:
        sample_email_body = f.read().strip()
    with open("life_automation/templates/self_description.yaml") as f:
        self_description = f.read().strip()
    USERS_COLLECTION.document("yogeshdevaggarwal@gmail.com").set(
        {
            "id": "yogeshdevaggarwal@gmail.com",
            "email": "yogeshdevaggarwal@gmail.com",
            "name": "Yogesh Aggarwal",
            "dp": "https://picsum.photos/seed/123/200/200",
            "credentials": {
                "google_oauth": None,
                "medium_oauth": None,
            },
            "data": {
                "selfDescription": self_description,
                "sampleEmail": {
                    "subject": "Referral request for a recent Backend Engineer job role (#3968102214)",
                    "body": sample_email_body,
                },
                "resumes": [
                    {
                        "title": "Backend developer",
                        "url": "https://google.com",
                        "dateCreated": 1726810330262,
                    },
                    {
                        "title": "Frontend developer",
                        "url": "https://google2.com",
                        "dateCreated": 1726810330262,
                    },
                ],
            },
        }
    )

    EMAIL_JOBS_COLLECTION.document("12345").set(
        {
            "id": "12345",
            "status": "WAITING",
            "userID": "yogeshdevaggarwal@gmail.com",
            "task": "GENERATE_EMAIL",
            "details": {
                "targetCompanyName": "PropertyLoop",
                "targetJobID": "3968102214",
                "targetJobLink": "https://www.linkedin.com/jobs/view/3968102214",
                "targetJobTitle": "Remote - Software (Next) Engineer (Next/React/Node/Typescript/MySQL)",
                "targetJobDescription": """
PropertyLoop is a rapidly growing technology business with the vision, resources, and team to become a global player in the property rental sector over the next 3-5 years.
Our platform was only recently launched, but we are already getting fantastic growth in inventory and customer numbers; we've been overwhelmed by the amazing feedback so far and our ambition is to build the best platform in the world for property transactions, and to expand our initially UK-based business into other countries.


We have an amazing technology team (20+ and growing quickly) developing our platform and we are looking for Senior Full stack Engineers (MERN) to help us in the next stage of our journey which includes mobile, scaling, containerisation and feature innovation.
The successful candidate will join a growing UK and India Development team as reporting to the Project Manager and VP of Engineering. The UK and India Development Team consists of several competencies including UX, QA, Developers and BAs.


Our current technologies include Azure, Node.js, React, Redux, Firebase & Typescript; we will build out our future stack from these (not immutable) core foundations, so in-depth experience and knowledge of all of these technologies is a pre-requisite.


Day to Day Responsibilities
Team management (task management and up-skilling)
Hands on development and code reviews and implementation of processes and strategies for delivering high quality features whilst continually reducing technical debt
Effectively communicating with the Product Owner, BA and Project manager to fully understand the requirements for the features
Inspiring other member of the development team with your knowledge and passion for technology
Guide and mentor within the team and provide feedback to the line managers around performance and reviews


Requirements
Must Have
Must have:
- Technical Architecture, Design, Development & Documentation
- Technical Leadership & Strategy
- Incident Management
- Agile Methodologies (SCRUM, Kanban, SAFe, etc.)


Experience working as a Full stack Engineer on product(s) with 1 million+ users across web and mobile applications
Experience with React/Node; including: MySQL/MySQL, Express, React, Redux, Node.js, TypeScript and hands on experience of developing with Google Firebase
An exceptional understanding of secure and scalable application development, including the full lifecycle of API microservices services, including authentication, API gateways and versioning
Strong enthusiasm for technology, you enjoy developing code in your own time and are up to date with current tools and best practices around development, DevOps and software management
Detailed, hands-on knowledge of CI/CD pipelines to automate builds and quality checks – ideally using Azure DevOps
An understanding of the necessity for accurate and up-to-date documentation for all processes and code repositories
Strong analytical skills to be able to break down complex problems into smaller atomic units of work and lead the planning and development of applications and features
Experience of designing secure and scalable web applications with appropriate unit test coverage
Experience mentoring team members and providing technical guidance
Conduct and participate in project planning & scheduling, design discussions, and provide assistance and prompt resolutions of issues during testing
Develop and manage well-functioning databases
Experience of using Docker to containerise applications and microservices
Excellent written and verbal communication skills with the ability to adjust your style and content to suit audiences at all levels, translating between technical and non-technical audiences; as necessary


Good to have
Experience of Ionic or similar hybrid mobile application development and release management
Experience of Azure cloud native solutions, including: App Service, Functions, Container Instances, Kubernetes, Managed Databases, CosmosDB, API Management
Experience of creating and deploying Azure infrastructure using the Azure CLI or Azure Portal
""",
                "targetPersonName": "Ibtesam",
                "targetPersonEmail": "yogeshdevaggarwal@gmail.com",
                "targetPersonPosition": "Backend Engineer",
                "targetPersonLinkedinProfileContent": "",
                "resumeURL": "https://google.com",
            },
            "result": None,
            "systemMessage": None,
            "dateCreated": 1726810330262,
            "dateUpdated": 1726810330262,
            "dateEmailSent": None,
        }
    )
