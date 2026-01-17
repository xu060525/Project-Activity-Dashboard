# My Personal Learning Diary

> This document records the knowledge I have gained during project development and learning, so that it will not be forgotten in the future.
>
> It is written as a diary and also serves as a technical reflection and engineering summary.
>
> Main topics include: **Python, FastAPI, Uvicorn, Web Applications, Software Engineering Practices**.

---

## Day 0: Environmental Configuration & Engineering Cognition

### Daily Theme
**Thinking like an engineer before writing code**

Day 0 was not about coding features. It was about understanding *what kind of project I am building* and *how professional software projects start*.

---

### Key Questions Asked

1. What is the nature of this project?
2. Why is a single `.py` script not suitable?
3. Why do we need a virtual environment?
4. How can this project be reproduced on another machine?

---

### Engineering-Oriented Answers

**Q1: What kind of project is this?**  
This is a **service-based project**, not a one-time script. The Python code runs continuously as a backend service and provides APIs and web data to clients.

**Q2: Why not just write one `.py` file?**  
Because the project has **multiple responsibilities**:
- Data collection
- Data processing
- API services
- Visualization
- Configuration & deployment

A single script cannot clearly separate concerns or scale with complexity.

**Q3: Why use a virtual environment?**  
A virtual environment provides:
- Dependency isolation
- Version consistency
- A clean and reproducible workspace

This ensures that the project can be reliably run on any machine in the future.

**Q4: How can others run this project?**  
By cloning the repository, creating a virtual environment, installing dependencies, and starting the service. This is a standard engineering workflow.

---

###  Key Knowledge Points

- **Service-based application** vs script-based program
- Importance of **reproducibility** in engineering
- Virtual environments (`venv`) as an industry standard
- Project root as a long-term maintainable workspace

---

### Day 0 Outcome

By the end of Day 0, I had:
- A clean project root directory
- An isolated Python virtual environment
- A clear understanding that engineering starts *before* coding

---

## Day 1: Project Structure & First FastAPI Service

### Daily Theme
**From Python code to a running backend service**

Day 1 focused on understanding how Python code becomes a real web service through structure, frameworks, and servers.

---

### Key Questions Asked

1. What is FastAPI’s role in this project?
2. What is the difference between an application and a server?
3. Why do we need an `app/` directory?
4. What does `app = FastAPI()` actually do?
5. Why do we start the project with `uvicorn` instead of `python main.py`?

---

### Engineering-Oriented Answers

**Q1: What is FastAPI’s role?**  
FastAPI is a **web framework** that handles HTTP communication, request routing, and response serialization. It allows developers to focus on business logic instead of protocol details.

**Q2: Application vs Server**  
- **FastAPI** defines the application (what to do when a request arrives)
- **Uvicorn** is the server that runs the application and listens for network requests

An application must be hosted by a server to be accessible.

**Q3: Why an `app/` directory?**  
The `app/` directory represents the **application boundary**. All core service logic lives inside it, which improves clarity, scalability, and maintainability.

**Q4: What does `app = FastAPI()` mean?**  
It creates and initializes an **application instance**, which holds routes, configuration, and middleware. Without this instance, no API can exist.

**Q5: Why `uvicorn app.main:app`?**  
Because we are not executing a script — we are **starting a service**. Uvicorn loads the FastAPI application and keeps it running to handle incoming HTTP requests.

---

### Key Knowledge Points

- Difference between **script execution** and **service execution**
- Role separation: framework vs server
- Importance of a clear project structure
- API as a long-running process

---

### Important Engineering Insight

> Writing backend code is not about “running a file”, but about **designing a system that stays alive, communicates, and evolves**.

---

### Day 1 Outcome

By the end of Day 1, I had:
- A professional backend project structure
- A running FastAPI service
- Auto-generated API documentation (`/docs`)
- A clearer understanding of real-world backend development

---

## Day 2: Configuration Management & First Dynamic API

### Daily Theme
**Separating configuration from code & building danamic APIs**

Day 2 focused on making the backend more flexible and professional by introducing configuration management and real parameter-driven APIs.

---

### Key Questions Asked
1. Why do we use `.env` files for configuration?
2. How does `{item_id}` in FastAPI routing actually work?
3. Why do we use `pydantic.BaseModel` for request bodies?

---

### Engineering-Oriented Answers

**Q1: Why use `.env` files?** 
Environment variables make static configuration easy to manage and centralized. Instead of searching through multiple files to change values, configuration can be adjusted in one place without touching application logic. This also improves security and deployment flexibility.

**Q2: How does `{item_id}` work in FastAPI?**  
`{item_id}` defines a **path parameter**. FastAPI automatically parses this part of the URL and injects it into the function as a typed variable. This allows each resource to be uniquely identified through its URL, following RESTful design principles.

**Q3: Why use `BaseModel`?**  
Because incoming data is unreliable. `pydantic.BaseModel` validates and cleans incoming JSON data, ensuring correct types, required fields, and predictable structure before the data enters business logic.

---

### Key Knowledge Points

- Environment variables decouple configuration from code
- RESTful APIs use URLs to uniquely identify resources
- Data validation is a backend responsibility, not a client responsibility
- FastAPI integrates validation and documentation automatically

---

### Day 2 Outcome

By the end of Day 2, I had:
- A configuration system based on `.env`
- A clear understanding of path parameters and query parameters
- My first POST API with structured request validation

---