"""
Question Bank for SkillSphere Automated Technical Assessment System.
Contains categorized MCQs with 4 options, 1 correct answer, difficulty level, and explanations.
"""

QUESTION_BANK = {
    "python": [
        # Beginner
        {
            "question": "What is the output of print(type([])) in Python?",
            "difficulty": "beginner",
            "options": ["<class 'list'>", "<class 'tuple'>", "<class 'array'>", "<class 'dict'>"],
            "correct_answer": "<class 'list'>",
            "explanation": "Square brackets [] in Python denote a list object."
        },
        {
            "question": "Which keyword is used to define an asynchronous function in Python?",
            "difficulty": "beginner",
            "options": ["async def", "await def", "thread def", "coroutine def"],
            "correct_answer": "async def",
            "explanation": "In Python 3.5+, asynchronous coroutines are defined using 'async def'."
        },
        {
            "question": "What is the primary difference between a list and a tuple in Python?",
            "difficulty": "beginner",
            "options": [
                "Lists are mutable while tuples are immutable",
                "Tuples are mutable while lists are immutable",
                "Lists cannot store heterogeneous data types",
                "Tuples cannot be indexed"
            ],
            "correct_answer": "Lists are mutable while tuples are immutable",
            "explanation": "Lists can be modified after creation (mutable), whereas tuples cannot be changed (immutable)."
        },
        {
            "question": "What does the PEP 8 standard represent in the Python ecosystem?",
            "difficulty": "beginner",
            "options": [
                "Style Guide for Python Code",
                "Python Package Manager Specification",
                "Asynchronous Event Loop Architecture",
                "Security Vulnerability Advisory Protocol"
            ],
            "correct_answer": "Style Guide for Python Code",
            "explanation": "PEP 8 is the official style guide for writing readable Python code."
        },
        {
            "question": "Which built-in function returns both the index and value when iterating over a sequence?",
            "difficulty": "beginner",
            "options": ["enumerate()", "zip()", "map()", "filter()"],
            "correct_answer": "enumerate()",
            "explanation": "enumerate() takes a collection and returns an enumerate object yielding tuples of (index, item)."
        },
        {
            "question": "How do you open a file in Python such that it is automatically closed after execution?",
            "difficulty": "beginner",
            "options": [
                "Using the 'with' statement (context manager)",
                "Using try...finally without with",
                "Calling file.auto_close()",
                "Passing mode='autoclose' to open()"
            ],
            "correct_answer": "Using the 'with' statement (context manager)",
            "explanation": "The 'with' statement guarantees proper acquisition and release of resources through context managers."
        },
        # Intermediate
        {
            "question": "What is the Global Interpreter Lock (GIL) in CPython?",
            "difficulty": "intermediate",
            "options": [
                "A mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once",
                "A compiler lock that prevents compilation of untrusted code",
                "A database transaction lock used in SQLAlchemy",
                "A security module preventing unauthorized socket binds"
            ],
            "correct_answer": "A mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once",
            "explanation": "The GIL is a mechanism used by CPython to ensure only one native thread executes bytecode at a time."
        },
        {
            "question": "What is the purpose of the '__slots__' attribute in a Python class?",
            "difficulty": "intermediate",
            "options": [
                "To optimize memory by preventing the creation of '__dict__' for instances",
                "To define private variables that cannot be accessed outside the module",
                "To specify abstract methods that subclasses must implement",
                "To register methods with the Python garbage collector"
            ],
            "correct_answer": "To optimize memory by preventing the creation of '__dict__' for instances",
            "explanation": "'__slots__' reserves space for a fixed set of attributes, eliminating dynamic per-instance dictionary overhead."
        },
        {
            "question": "In Python decorators, what does functools.wraps do?",
            "difficulty": "intermediate",
            "options": [
                "Preserves the original function's name, docstring, and metadata",
                "Enforces strict type checking on decorator arguments",
                "Runs the decorated function inside a background thread pool",
                "Caches the output of the function using memoization"
            ],
            "correct_answer": "Preserves the original function's name, docstring, and metadata",
            "explanation": "functools.wraps copies the __name__, __doc__, and other attributes from the decorated function to the wrapper."
        },
        {
            "question": "What does a generator function yield instead of return in Python?",
            "difficulty": "intermediate",
            "options": [
                "Yields a generator iterator producing values on demand (lazy evaluation)",
                "Returns a full list loaded directly into RAM",
                "Yields a socket connection handle",
                "Throws a StopIteration exception immediately"
            ],
            "correct_answer": "Yields a generator iterator producing values on demand (lazy evaluation)",
            "explanation": "Generators produce sequence items lazily when iterated, using minimal memory."
        },
        {
            "question": "In FastAPI, what library powers request validation and data serialization?",
            "difficulty": "intermediate",
            "options": ["Pydantic", "Marshmallow", "Cerberus", "Schema"],
            "correct_answer": "Pydantic",
            "explanation": "FastAPI is built tightly on top of Starlette and Pydantic for data parsing and validation."
        },
        {
            "question": "What is the time complexity of looking up a key in a standard Python dictionary?",
            "difficulty": "intermediate",
            "options": ["O(1) average case", "O(n) average case", "O(log n) average case", "O(n^2) worst case only"],
            "correct_answer": "O(1) average case",
            "explanation": "Python dicts are implemented as hash tables, providing O(1) average time complexity for lookups."
        },
        {
            "question": "What is method resolution order (MRO) in Python, and how is it determined?",
            "difficulty": "intermediate",
            "options": [
                "Using the C3 Linearization algorithm",
                "Alphabetical order of parent class names",
                "Depth-first search strictly from left to right",
                "Randomized hashing order of classes"
            ],
            "correct_answer": "Using the C3 Linearization algorithm",
            "explanation": "Python 2.3+ uses the C3 Linearization algorithm to determine method resolution order."
        },
        # Advanced
        {
            "question": "How does Python's cyclical garbage collector detect circular references?",
            "difficulty": "advanced",
            "options": [
                "By tracking container objects in doubly linked lists and analyzing reference counts minus intra-cycle references",
                "By using mark-and-sweep strictly on primitive types",
                "By terminating processes whenever recursion depth exceeds 1000",
                "By inspecting thread execution stacks on every context switch"
            ],
            "correct_answer": "By tracking container objects in doubly linked lists and analyzing reference counts minus intra-cycle references",
            "explanation": "CPython's cyclic GC isolates reference cycles among container objects by calculating effective external references."
        },
        {
            "question": "What is the behavior of asyncio.gather() when return_exceptions=True?",
            "difficulty": "advanced",
            "options": [
                "Exceptions are treated as successful results and included in the return list without aborting remaining tasks",
                "The entire gather operation fails immediately on the first exception",
                "Exceptions are suppressed and replaced by None in the result list",
                "The event loop is shut down cleanly"
            ],
            "correct_answer": "Exceptions are treated as successful results and included in the return list without aborting remaining tasks",
            "explanation": "When return_exceptions=True, exceptions are captured and placed in the result array alongside successful returns."
        },
        {
            "question": "What happens under the hood when a Python function uses the 'yield from' expression?",
            "difficulty": "advanced",
            "options": [
                "It establishes a bi-directional transparent channel between caller and subgenerator, delegating iteration and values",
                "It converts the subgenerator into a synchronous list comprehension",
                "It spawns an OS worker thread to consume the generator",
                "It raises a GeneratorExit exception to close outer iterations"
            ],
            "correct_answer": "It establishes a bi-directional transparent channel between caller and subgenerator, delegating iteration and values",
            "explanation": "'yield from' transparently delegates sending values, exceptions, and return values between outer caller and inner generator."
        },
        {
            "question": "What is a Python metaclass?",
            "difficulty": "advanced",
            "options": [
                "The class of a class, defining how classes themselves are constructed and behaved",
                "A special base class that provides automatic database ORM mappings",
                "A compiler directive that compiles Python directly to C bytecode",
                "A security sandbox wrapper around untrusted third-party imports"
            ],
            "correct_answer": "The class of a class, defining how classes themselves are constructed and behaved",
            "explanation": "A metaclass inherits from type and controls the creation, attributes, and behavior of class objects."
        },
        {
            "question": "How does contextvars module differ from threading.local() in Python?",
            "difficulty": "advanced",
            "options": [
                "contextvars supports context isolation across asynchronous coroutines as well as threads",
                "threading.local is async-safe while contextvars is not",
                "contextvars can only store integer primitives",
                "threading.local is deprecated and removed in modern Python"
            ],
            "correct_answer": "contextvars supports context isolation across asynchronous coroutines as well as threads",
            "explanation": "contextvars is designed specifically to track context correctly through asynchronous event loop context switches."
        },
        {
            "question": "In SQLAlchemy, what is the primary role of the Unit of Work pattern?",
            "difficulty": "advanced",
            "options": [
                "Maintaining a list of objects affected by a transaction and coordinating writing changes atomically",
                "Automatically generating SQL migration files on schema change",
                "Managing connection pooling across multiple PostgreSQL read replicas",
                "Compiling raw Python AST into optimized C extensions"
            ],
            "correct_answer": "Maintaining a list of objects affected by a transaction and coordinating writing changes atomically",
            "explanation": "The Unit of Work pattern tracks pending inserts, updates, and deletes, committing them in an optimal ordered batch."
        },
        {
            "question": "Which Python dunder method is called when an attribute is NOT found in an object's instance dictionary or class tree?",
            "difficulty": "advanced",
            "options": ["__getattr__", "__getattribute__", "__setattr__", "__getitem__"],
            "correct_answer": "__getattr__",
            "explanation": "__getattr__ is only invoked as a fallback when the attribute does not exist, unlike __getattribute__ which is always called."
        }
    ],

    "react": [
        # Beginner
        {
            "question": "What is the primary purpose of the Virtual DOM in React?",
            "difficulty": "beginner",
            "options": [
                "To optimize rendering performance by minimizing direct expensive real DOM manipulations",
                "To store global Redux state in browser localStorage automatically",
                "To compile JSX directly into WebAssembly machine code",
                "To replace standard HTML elements with canvas drawings"
            ],
            "correct_answer": "To optimize rendering performance by minimizing direct expensive real DOM manipulations",
            "explanation": "React compares virtual DOM snapshots (diffing) and batches updates to the real DOM."
        },
        {
            "question": "Which hook is used to perform side effects in functional React components?",
            "difficulty": "beginner",
            "options": ["useEffect", "useState", "useMemo", "useContext"],
            "correct_answer": "useEffect",
            "explanation": "useEffect handles side effects like API requests, DOM manipulation, timers, and subscriptions."
        },
        {
            "question": "Why must list items in React have a unique 'key' prop?",
            "difficulty": "beginner",
            "options": [
                "To help React identify which items have changed, added, or removed during reconciliation",
                "To automatically sort the array in ascending alphabetical order",
                "To encrypt component props for security during transmission",
                "To register the DOM element with CSS selectors"
            ],
            "correct_answer": "To help React identify which items have changed, added, or removed during reconciliation",
            "explanation": "Keys provide identity to elements across renders, enabling efficient DOM reuse."
        },
        {
            "question": "What happens when you call useState in a React component?",
            "difficulty": "beginner",
            "options": [
                "It returns a stateful value and an updater function that triggers a component re-render when called",
                "It writes the value directly to the browser window object",
                "It sends an AJAX POST request to the backend server",
                "It pauses execution of the JavaScript thread until resolved"
            ],
            "correct_answer": "It returns a stateful value and an updater function that triggers a component re-render when called",
            "explanation": "useState returns a 2-element tuple [state, setState] where setState schedules a re-render."
        },
        {
            "question": "What is JSX in React?",
            "difficulty": "beginner",
            "options": [
                "A syntax extension to JavaScript that resembles HTML and compiles to React.createElement()",
                "A standalone templating language compiled exclusively on the server",
                "A proprietary CSS preprocessor similar to Sass",
                "A database query language for GraphQL"
            ],
            "correct_answer": "A syntax extension to JavaScript that resembles HTML and compiles to React.createElement()",
            "explanation": "JSX lets developers write HTML-like markup directly inside JavaScript files."
        },
        {
            "question": "How are props passed from a parent component to a child in React?",
            "difficulty": "beginner",
            "options": [
                "As attributes in JSX syntax (e.g. <Child title='Hello' />)",
                "By modifying global window variables",
                "By importing the child's internal state function",
                "Through WebSocket events only"
            ],
            "correct_answer": "As attributes in JSX syntax (e.g. <Child title='Hello' />)",
            "explanation": "Props are passed as attributes down the component hierarchy."
        },
        # Intermediate
        {
            "question": "What is the difference between useMemo and useCallback?",
            "difficulty": "intermediate",
            "options": [
                "useMemo memoizes the computed result value, while useCallback memoizes the function definition itself",
                "useCallback memoizes computed values, while useMemo memoizes DOM refs",
                "useMemo can only be used with class components",
                "useCallback executes side effects like API calls on mount"
            ],
            "correct_answer": "useMemo memoizes the computed result value, while useCallback memoizes the function definition itself",
            "explanation": "useMemo cache-stores a calculated value; useCallback cache-stores a callback function reference across renders."
        },
        {
            "question": "What is the React Reconciliation algorithm also known as?",
            "difficulty": "intermediate",
            "options": ["React Fiber", "Redux Flux", "Shadow DOM", "Hydration Engine"],
            "correct_answer": "React Fiber",
            "explanation": "React Fiber is the complete rewrite of React's reconciliation engine introduced to enable incremental rendering."
        },
        {
            "question": "When should you use the useRef hook in React?",
            "difficulty": "intermediate",
            "options": [
                "To access imperative DOM nodes or persist mutable values across renders without triggering a re-render",
                "To fetch data asynchronously from REST endpoints",
                "To bind Redux action creators to dispatch",
                "To define component routing paths in React Router"
            ],
            "correct_answer": "To access imperative DOM nodes or persist mutable values across renders without triggering a re-render",
            "explanation": "useRef holds a mutable object whose .current property persists without causing component re-render when mutated."
        },
        {
            "question": "In React 18, what is Automatic Batching?",
            "difficulty": "intermediate",
            "options": [
                "Batching multiple state updates inside promises, timeouts, and native event handlers into a single re-render",
                "Batching API network calls into one HTTP request",
                "Automatically compiling Tailwind CSS classes into a single file",
                "Combining multiple React contexts into one provider"
            ],
            "correct_answer": "Batching multiple state updates inside promises, timeouts, and native event handlers into a single re-render",
            "explanation": "React 18 batches all state updates regardless of where they originate (async callbacks, timeouts, promises)."
        },
        {
            "question": "What problem does React Context solve?",
            "difficulty": "intermediate",
            "options": [
                "Prop drilling across deeply nested component hierarchies",
                "Slow network transfer speeds on mobile devices",
                "Cross-site scripting (XSS) vulnerabilities in forms",
                "Memory leaks in unmounted canvas elements"
            ],
            "correct_answer": "Prop drilling across deeply nested component hierarchies",
            "explanation": "Context provides a way to share data globally across the component tree without manually passing props at every level."
        },
        {
            "question": "What is the cleanup function returned by useEffect used for?",
            "difficulty": "intermediate",
            "options": [
                "To clean up timers, subscriptions, or event listeners when the component unmounts or before re-running the effect",
                "To garbage collect unused variables inside the Redux store",
                "To reset all component state variables to null",
                "To flush browser cache memory"
            ],
            "correct_answer": "To clean up timers, subscriptions, or event listeners when the component unmounts or before re-running the effect",
            "explanation": "The cleanup function prevents memory leaks by canceling pending asynchronous operations when the component unmounts."
        },
        {
            "question": "What is a React Higher-Order Component (HOC)?",
            "difficulty": "intermediate",
            "options": [
                "A function that takes a component and returns a new enhanced component",
                "A component placed exclusively at the root of the application",
                "A component that renders SVG animations with GSAP",
                "A backend microservice handling server-side rendering"
            ],
            "correct_answer": "A function that takes a component and returns a new enhanced component",
            "explanation": "An HOC is an advanced pattern in React for reusing component logic (e.g. withAuth(Dashboard))."
        },
        # Advanced
        {
            "question": "In React Concurrent Mode, what does the useTransition hook do?",
            "difficulty": "advanced",
            "options": [
                "Marks non-urgent state updates as transitions, keeping the user interface responsive during heavy renders",
                "Animates CSS transitions using hardware-accelerated transforms",
                "Transitions users between authenticated and unauthenticated routes",
                "Executes database migrations during server-side hydration"
            ],
            "correct_answer": "Marks non-urgent state updates as transitions, keeping the user interface responsive during heavy renders",
            "explanation": "useTransition separates urgent updates (e.g. typing) from non-urgent transitions (e.g. filtering a long list)."
        },
        {
            "question": "What is selective hydration in React 18 Server-Side Rendering with Suspense?",
            "difficulty": "advanced",
            "options": [
                "Allowing parts of the page to hydrate independently without waiting for all HTML or JavaScript to finish loading",
                "Hydrating only the CSS stylesheets before rendering DOM nodes",
                "Enabling hydration only for desktop viewports",
                "Rehydrating Redux state from IndexedDB"
            ],
            "correct_answer": "Allowing parts of the page to hydrate independently without waiting for all HTML or JavaScript to finish loading",
            "explanation": "With Suspense and React 18 streaming SSR, browser can hydrate ready components early based on user interaction."
        },
        {
            "question": "How does React Fiber achieve interruptible rendering?",
            "difficulty": "advanced",
            "options": [
                "By breaking work into units of work on a singly linked list tree and using cooperative scheduling (requestIdleCallback / MessageChannel)",
                "By spawning multi-threaded Web Workers for each virtual DOM node",
                "By caching full DOM trees in GPU memory",
                "By preventing JavaScript event loop execution"
            ],
            "correct_answer": "By breaking work into units of work on a singly linked list tree and using cooperative scheduling (requestIdleCallback / MessageChannel)",
            "explanation": "Fiber structures work as a linked list of fibers, allowing the scheduler to pause, abort, or prioritize work."
        },
        {
            "question": "What is the difference between useEffect and useLayoutEffect?",
            "difficulty": "advanced",
            "options": [
                "useLayoutEffect runs synchronously immediately after all DOM mutations but before the browser paints",
                "useEffect runs before DOM mutations occur",
                "useLayoutEffect runs asynchronously in a web worker",
                "useEffect can only be used with SVG elements"
            ],
            "correct_answer": "useLayoutEffect runs synchronously immediately after all DOM mutations but before the browser paints",
            "explanation": "useLayoutEffect fires synchronously after render before visual painting, preventing visual flickers when measuring DOM."
        },
        {
            "question": "What is an Error Boundary in React, and which lifecycle method must it implement?",
            "difficulty": "advanced",
            "options": [
                "A class component implementing componentDidCatch or static getDerivedStateFromError",
                "A functional hook called useErrorBoundary()",
                "A middleware configured in Vite configuration",
                "A global window.onerror listener"
            ],
            "correct_answer": "A class component implementing componentDidCatch or static getDerivedStateFromError",
            "explanation": "Error boundaries catch JavaScript errors anywhere in their child component tree and display fallback UI."
        },
        {
            "question": "What is the purpose of React Server Components (RSC)?",
            "difficulty": "advanced",
            "options": [
                "Components that execute and render exclusively on the server, sending zero JavaScript bundle to the client",
                "Components that replace Node.js Express servers completely",
                "Components designed to manage local SQLite databases in the browser",
                "Components that only handle WebSocket connections"
            ],
            "correct_answer": "Components that execute and render exclusively on the server, sending zero JavaScript bundle to the client",
            "explanation": "RSCs execute strictly on the server, accessing databases directly without shipping their code to client bundles."
        },
        {
            "question": "What is the React 'Rules of Hooks' requirement regarding call order?",
            "difficulty": "advanced",
            "options": [
                "Hooks must be called at the top level and in the exact same order on every render",
                "Hooks can be called inside conditional statements if wrapped in try/catch",
                "Hooks must always be declared in alphabetical order",
                "Hooks can only be called from inside nested loop iterations"
            ],
            "correct_answer": "Hooks must be called at the top level and in the exact same order on every render",
            "explanation": "React relies on the call order of hooks to preserve internal state arrays between consecutive renders."
        }
    ],

    "fullstack_mern": [
        # Beginner
        {
            "question": "What does the MERN stack acronym stand for?",
            "difficulty": "beginner",
            "options": [
                "MongoDB, Express.js, React.js, Node.js",
                "MySQL, Ember.js, React.js, Next.js",
                "MongoDB, Electron.js, Redux, Node.js",
                "MariaDB, Express.js, Ruby, Nginx"
            ],
            "correct_answer": "MongoDB, Express.js, React.js, Node.js",
            "explanation": "MERN stands for MongoDB (database), Express.js (backend framework), React.js (frontend library), and Node.js (runtime)."
        },
        {
            "question": "What is Express.js middleware in a Node.js server?",
            "difficulty": "beginner",
            "options": [
                "Functions that have access to request and response objects and can modify them or terminate the request-response cycle",
                "A database engine for storing sessions",
                "A CSS styling engine for server templates",
                "A compiler that translates TypeScript into JavaScript"
            ],
            "correct_answer": "Functions that have access to request and response objects and can modify them or terminate the request-response cycle",
            "explanation": "Middleware functions execute sequentially in the Express request pipeline, calling next() to continue."
        },
        {
            "question": "In MongoDB, what is a document?",
            "difficulty": "beginner",
            "options": [
                "A BSON record composed of field-value pairs, analogous to a JSON object",
                "A PDF file stored on disk",
                "A relational table schema definition",
                "An SQL stored procedure"
            ],
            "correct_answer": "A BSON record composed of field-value pairs, analogous to a JSON object",
            "explanation": "MongoDB stores data records as BSON documents grouped inside collections."
        },
        {
            "question": "Which Node.js core module is used to create an HTTP server?",
            "difficulty": "beginner",
            "options": ["http", "net", "url", "fs"],
            "correct_answer": "http",
            "explanation": "The 'http' module in Node.js provides utilities to create HTTP servers and client requests."
        },
        {
            "question": "What is npm in the Node.js ecosystem?",
            "difficulty": "beginner",
            "options": [
                "Node Package Manager",
                "Node Performance Monitor",
                "Network Protocol Module",
                "Native Process Manager"
            ],
            "correct_answer": "Node Package Manager",
            "explanation": "npm is the default package manager for JavaScript and the Node.js runtime environment."
        },
        {
            "question": "How does Node.js achieve asynchronous non-blocking I/O?",
            "difficulty": "beginner",
            "options": [
                "Using an event-driven architecture powered by the libuv event loop",
                "By launching a separate OS process for every network connection",
                "By executing multiple parallel threads in pure JavaScript",
                "By disabling disk access completely"
            ],
            "correct_answer": "Using an event-driven architecture powered by the libuv event loop",
            "explanation": "Node.js utilizes a single-threaded event loop backed by the multi-threaded libuv C library for I/O operations."
        },
        # Intermediate
        {
            "question": "What is the difference between MongoDB findOneAndUpdate and updateOne?",
            "difficulty": "intermediate",
            "options": [
                "findOneAndUpdate can return the document as it was before or after update, while updateOne only returns status metadata",
                "updateOne returns the updated document, while findOneAndUpdate cannot",
                "findOneAndUpdate is deprecated in MongoDB 5.0",
                "updateOne executes synchronously while findOneAndUpdate is asynchronous"
            ],
            "correct_answer": "findOneAndUpdate can return the document as it was before or after update, while updateOne only returns status metadata",
            "explanation": "findOneAndUpdate returns the actual document (with returnDocument: 'after' option) atomically."
        },
        {
            "question": "What are the phases of the Node.js Event Loop?",
            "difficulty": "intermediate",
            "options": [
                "Timers, Pending callbacks, Idle/Prepare, Poll, Check, Close callbacks",
                "Fetch, Decode, Execute, Writeback",
                "Input, Processing, Output, Storage",
                "Compile, Link, Load, Execute"
            ],
            "correct_answer": "Timers, Pending callbacks, Idle/Prepare, Poll, Check, Close callbacks",
            "explanation": "The libuv event loop operates in specific sequential phases: timers, pending I/O callbacks, poll, check (setImmediate), and close."
        },
        {
            "question": "In Express.js, what is the role of next(err) when passed an error argument?",
            "difficulty": "intermediate",
            "options": [
                "It skips all remaining non-error middleware and jumps directly to error-handling middleware",
                "It crashes the server process immediately",
                "It sends an HTTP 200 response to the client",
                "It restarts the Node.js application"
            ],
            "correct_answer": "It skips all remaining non-error middleware and jumps directly to error-handling middleware",
            "explanation": "Express treats any argument passed to next() as an error and routes execution to registered (err, req, res, next) handlers."
        },
        {
            "question": "What is an index in MongoDB, and what is its primary data structure?",
            "difficulty": "intermediate",
            "options": [
                "A B-tree structure that stores a small portion of the collection's dataset to accelerate query execution",
                "A flat text file containing database logs",
                "A hash map stored exclusively in browser localStorage",
                "An array of string tokens indexed with binary search"
            ],
            "correct_answer": "A B-tree structure that stores a small portion of the collection's dataset to accelerate query execution",
            "explanation": "MongoDB indexes use B-trees to support high-efficiency range and equality queries."
        },
        {
            "question": "How should passwords be securely stored in a MERN stack application?",
            "difficulty": "intermediate",
            "options": [
                "Salted and hashed using bcrypt or Argon2",
                "Encrypted using Base64 encoding",
                "Stored in plain text inside an environment variable",
                "Hashed with standard MD5 without salt"
            ],
            "correct_answer": "Salted and hashed using bcrypt or Argon2",
            "explanation": "Passwords must be hashed with a cryptographic work factor and unique salt using algorithms like bcrypt or Argon2."
        },
        {
            "question": "What is CORS (Cross-Origin Resource Sharing) in web applications?",
            "difficulty": "intermediate",
            "options": [
                "A browser security mechanism that uses HTTP headers to allow or restrict resources requested from another domain",
                "A database replication protocol across multiple cloud providers",
                "A data compression format for JSON payloads",
                "A caching algorithm used by CDNs"
            ],
            "correct_answer": "A browser security mechanism that uses HTTP headers to allow or restrict resources requested from another domain",
            "explanation": "CORS prevents malicious websites from reading sensitive responses from third-party servers via the browser."
        },
        {
            "question": "In Node.js, what is the difference between process.nextTick() and setImmediate()?",
            "difficulty": "intermediate",
            "options": [
                "process.nextTick executes immediately after the current operation before the event loop continues; setImmediate runs in the check phase",
                "setImmediate executes before any I/O can be processed",
                "process.nextTick is only available in browser environments",
                "There is no difference between them"
            ],
            "correct_answer": "process.nextTick executes immediately after the current operation before the event loop continues; setImmediate runs in the check phase",
            "explanation": "nextTick queue is processed immediately after the current phase completes, before moving to the next event loop phase."
        },
        # Advanced
        {
            "question": "What is a MongoDB replica set and how is high availability achieved?",
            "difficulty": "advanced",
            "options": [
                "A cluster of MongoDB instances with one Primary and multiple Secondaries that hold elections via the Raft-based consensus protocol if the primary fails",
                "A load balancer distributing HTTP requests to Node.js instances",
                "A Docker container cluster running behind Nginx",
                "A relational table partitioning technique"
            ],
            "correct_answer": "A cluster of MongoDB instances with one Primary and multiple Secondaries that hold elections via the Raft-based consensus protocol if the primary fails",
            "explanation": "MongoDB replica sets replicate oplogs across nodes and hold automated failover elections within seconds."
        },
        {
            "question": "In Node.js, what is backpressure in the context of Streams?",
            "difficulty": "advanced",
            "options": [
                "When data is written faster than the consumer stream can process, signaling the readable stream to pause",
                "CPU throttling when server temperature exceeds safety limits",
                "Database deadlock caused by simultaneous write transactions",
                "Browser memory crashing due to excessive DOM nodes"
            ],
            "correct_answer": "When data is written faster than the consumer stream can process, signaling the readable stream to pause",
            "explanation": "Backpressure regulates data flow between streams to prevent RAM overflow when reading faster than writing."
        },
        {
            "question": "What is the MongoDB Aggregation Pipeline?",
            "difficulty": "advanced",
            "options": [
                "A framework for data modeling and transformation where documents pass through a multi-stage pipeline ($match, $group, $project)",
                "A backup script that exports databases to S3",
                "A real-time socket connection for live chat messages",
                "A middleware that compresses HTTP responses with gzip"
            ],
            "correct_answer": "A framework for data modeling and transformation where documents pass through a multi-stage pipeline ($match, $group, $project)",
            "explanation": "The aggregation pipeline transforms documents through successive stages like $match, $group, $unwind, and $project."
        },
        {
            "question": "How does Node.js Clustering module scale applications across multi-core processors?",
            "difficulty": "advanced",
            "options": [
                "By forking multiple child processes sharing server ports using IPC and distributing connections round-robin",
                "By enabling multi-threading inside the V8 JavaScript engine",
                "By increasing JavaScript call stack size dynamically",
                "By offloading compilation to a remote cloud worker"
            ],
            "correct_answer": "By forking multiple child processes sharing server ports using IPC and distributing connections round-robin",
            "explanation": "Cluster spawns multiple Node.js worker processes (one per CPU core) that share listen sockets via the master process."
        },
        {
            "question": "What is the risk of an unindexed $sort operation in MongoDB?",
            "difficulty": "advanced",
            "options": [
                "It performs an in-memory sort that throws an error if it exceeds the 100MB RAM limit (without allowDiskUse)",
                "It corrupts database indexes irreversibly",
                "It drops the target collection automatically",
                "It locks the entire database indefinitely"
            ],
            "correct_answer": "It performs an in-memory sort that throws an error if it exceeds the 100MB RAM limit (without allowDiskUse)",
            "explanation": "MongoDB limits in-memory sort operations to 100MB unless backed by an index or allowDiskUse is enabled."
        },
        {
            "question": "What is JWT signature tampering, and how is it prevented?",
            "difficulty": "advanced",
            "options": [
                "Modifying token payload claims; prevented because the cryptographic HMAC/RSA signature will fail verification without the secret key",
                "By encrypting the entire token with Base64",
                "By storing the JWT in an unencrypted cookie",
                "By making the JWT expire every 5 seconds"
            ],
            "correct_answer": "Modifying token payload claims; prevented because the cryptographic HMAC/RSA signature will fail verification without the secret key",
            "explanation": "The cryptographic signature header.payload hash verified by the secret key ensures payload integrity."
        },
        {
            "question": "In Node.js, how can you diagnose and identify a memory leak in production?",
            "difficulty": "advanced",
            "options": [
                "By capturing heap snapshots using v8.getHeapSnapshot() or Chrome DevTools and comparing retained object trees",
                "By restarting the server every hour with cron",
                "By reading the package.json file",
                "By checking the git commit history"
            ],
            "correct_answer": "By capturing heap snapshots using v8.getHeapSnapshot() or Chrome DevTools and comparing retained object trees",
            "explanation": "Comparing heap snapshots reveals retaining paths of objects that are not being freed by garbage collection."
        }
    ],

    "java": [
        # Beginner
        {
            "question": "What is the primary difference between JDK, JRE, and JVM in Java?",
            "difficulty": "beginner",
            "options": [
                "JDK is for development, JRE is the execution environment, and JVM executes bytecode",
                "JVM is for development, JDK executes bytecode, and JRE is the database driver",
                "There is no difference; they are interchangeable terms",
                "JDK is deprecated in Java 17"
            ],
            "correct_answer": "JDK is for development, JRE is the execution environment, and JVM executes bytecode",
            "explanation": "JDK contains development tools and JRE; JRE contains JVM and libraries; JVM runs the bytecode."
        },
        {
            "question": "Which access modifier in Java restricts visibility to only within the same class?",
            "difficulty": "beginner",
            "options": ["private", "protected", "public", "default (package-private)"],
            "correct_answer": "private",
            "explanation": "The private modifier specifies that the member can only be accessed in its own class."
        },
        {
            "question": "What is the default value of a boolean primitive variable in Java?",
            "difficulty": "beginner",
            "options": ["false", "true", "null", "0"],
            "correct_answer": "false",
            "explanation": "The default value of an uninitialized primitive boolean field in Java is false."
        },
        {
            "question": "What does the 'final' keyword signify when applied to a variable in Java?",
            "difficulty": "beginner",
            "options": [
                "Its reference or primitive value cannot be changed once initialized",
                "It can only be used by one thread at a time",
                "It is automatically stored in permanent memory",
                "It will be deleted by the garbage collector immediately"
            ],
            "correct_answer": "Its reference or primitive value cannot be changed once initialized",
            "explanation": "A final variable becomes a constant whose reference cannot be reassigned."
        },
        {
            "question": "Which interface must a class implement to be iterable using an enhanced for-loop in Java?",
            "difficulty": "beginner",
            "options": ["Iterable", "Collection", "Iterator", "List"],
            "correct_answer": "Iterable",
            "explanation": "Implementing java.lang.Iterable allows an object to be the target of the enhanced for-loop."
        },
        {
            "question": "What is the difference between String, StringBuilder, and StringBuffer in Java?",
            "difficulty": "beginner",
            "options": [
                "String is immutable; StringBuilder is mutable and non-thread-safe; StringBuffer is mutable and synchronized (thread-safe)",
                "String is mutable; StringBuilder is immutable",
                "StringBuffer is faster than StringBuilder in single-threaded environments",
                "StringBuilder cannot store Unicode characters"
            ],
            "correct_answer": "String is immutable; StringBuilder is mutable and non-thread-safe; StringBuffer is mutable and synchronized (thread-safe)",
            "explanation": "StringBuilder avoids synchronization overhead, while StringBuffer uses synchronized methods for thread safety."
        },
        # Intermediate
        {
            "question": "In Java Spring Boot, what does the @Autowired annotation do?",
            "difficulty": "intermediate",
            "options": [
                "Injects matching dependencies automatically into beans via Spring's dependency injection container",
                "Creates a new database table on startup",
                "Encrypts method return values",
                "Maps HTTP GET requests to handler methods"
            ],
            "correct_answer": "Injects matching dependencies automatically into beans via Spring's dependency injection container",
            "explanation": "@Autowired marks a constructor, field, or setter method to be autowired by Spring's DI engine."
        },
        {
            "question": "What is the contract between equals() and hashCode() in Java?",
            "difficulty": "intermediate",
            "options": [
                "If two objects are equal according to equals(), they MUST have the same hashCode()",
                "If two objects have the same hashCode(), they MUST be equal according to equals()",
                "equals() and hashCode() can never be overridden together",
                "hashCode() must always return a positive prime number"
            ],
            "correct_answer": "If two objects are equal according to equals(), they MUST have the same hashCode()",
            "explanation": "Equal objects must have equal hash codes to maintain consistency in hash-based collections (HashMap, HashSet)."
        },
        {
            "question": "What is the difference between Comparable and Comparator interfaces in Java?",
            "difficulty": "intermediate",
            "options": [
                "Comparable defines natural ordering via compareTo(obj), while Comparator defines custom external ordering via compare(o1, o2)",
                "Comparator can only compare integer values",
                "Comparable cannot be implemented by user classes",
                "Comparator modifies the original collection directly"
            ],
            "correct_answer": "Comparable defines natural ordering via compareTo(obj), while Comparator defines custom external ordering via compare(o1, o2)",
            "explanation": "Comparable modifies the class itself (natural ordering), whereas Comparator provides external flexible sorting strategies."
        },
        {
            "question": "What is a Checked Exception in Java?",
            "difficulty": "intermediate",
            "options": [
                "An exception checked at compile-time that must be either caught or declared in the throws clause",
                "An exception that only occurs in multi-threaded code",
                "An unchecked runtime error like NullPointerException",
                "A hardware fault that crashes the JVM immediately"
            ],
            "correct_answer": "An exception checked at compile-time that must be either caught or declared in the throws clause",
            "explanation": "Checked exceptions (inheriting from Exception but not RuntimeException) require compile-time handling."
        },
        {
            "question": "What is the Java Stream API, introduced in Java 8?",
            "difficulty": "intermediate",
            "options": [
                "A functional-style pipeline for processing collections of objects with operations like map, filter, and reduce",
                "A network socket protocol for streaming audio files",
                "A file input/output replacement for java.io",
                "A multithreaded GUI framework for desktop apps"
            ],
            "correct_answer": "A functional-style pipeline for processing collections of objects with operations like map, filter, and reduce",
            "explanation": "Stream API allows declarative data processing over sequences of elements using functional expressions."
        },
        {
            "question": "What is the purpose of the 'volatile' keyword in Java multithreading?",
            "difficulty": "intermediate",
            "options": [
                "Guarantees visibility of variable updates across multiple threads by reading/writing directly to main memory",
                "Locks the object monitor exclusively like synchronized",
                "Prevents the variable from being serialized",
                "Allocates the variable in CPU registers permanently"
            ],
            "correct_answer": "Guarantees visibility of variable updates across multiple threads by reading/writing directly to main memory",
            "explanation": "volatile ensures changes made by one thread are immediately visible to other threads, avoiding CPU cache staleness."
        },
        {
            "question": "In Spring Boot, what is the default scope of a Spring Bean?",
            "difficulty": "intermediate",
            "options": ["Singleton", "Prototype", "Request", "Session"],
            "correct_answer": "Singleton",
            "explanation": "By default, Spring creates a single shared instance (Singleton) for each defined bean."
        },
        # Advanced
        {
            "question": "How does the G1 (Garbage-First) Garbage Collector work in modern JVMs?",
            "difficulty": "advanced",
            "options": [
                "It partitions the heap into equal-sized regions and prioritizes collecting regions with the most garbage to meet target pause times",
                "It pauses all threads until the entire heap is cleared",
                "It only collects objects in the permanent generation",
                "It uses pure reference counting without generational analysis"
            ],
            "correct_answer": "It partitions the heap into equal-sized regions and prioritizes collecting regions with the most garbage to meet target pause times",
            "explanation": "G1 divides the heap into regions and targets regions filled with the most reclaimable space first."
        },
        {
            "question": "What is the Java Memory Model (JMM) 'happens-before' relationship?",
            "difficulty": "advanced",
            "options": [
                "A formal specification ensuring that memory writes by one action are visible to another specified read action",
                "A compiler optimization that reorders lines of code alphabetically",
                "A memory allocation strategy for large arrays",
                "A garbage collection threshold parameter"
            ],
            "correct_answer": "A formal specification ensuring that memory writes by one action are visible to another specified read action",
            "explanation": "Happens-before order guarantees memory visibility between operations across concurrent threads."
        },
        {
            "question": "What happens during class loading in the JVM?",
            "difficulty": "advanced",
            "options": [
                "Loading (reading binary bytecode), Linking (Verification, Preparation, Resolution), and Initialization (executing static initializers)",
                "Compiling Java source directly into x86 machine instructions",
                "Uploading class files to a remote repository",
                "Allocating maximum heap memory to each method"
            ],
            "correct_answer": "Loading (reading binary bytecode), Linking (Verification, Preparation, Resolution), and Initialization (executing static initializers)",
            "explanation": "The three class loading phases are Loading, Linking (verify, prepare, resolve), and Initialization."
        },
        {
            "question": "What is the difference between synchronized block and java.util.concurrent.locks.ReentrantLock?",
            "difficulty": "advanced",
            "options": [
                "ReentrantLock provides tryLock() timeout capabilities, fairness policies, and interruptible locks not available with synchronized",
                "synchronized is faster in all high-contention scenarios",
                "ReentrantLock does not require explicit unlocking in finally blocks",
                "synchronized cannot be used on instance methods"
            ],
            "correct_answer": "ReentrantLock provides tryLock() timeout capabilities, fairness policies, and interruptible locks not available with synchronized",
            "explanation": "ReentrantLock provides advanced features like timed lock acquisition, interruptibility, and fair queuing."
        },
        {
            "question": "What are Java Virtual Threads (Project Loom, Java 21)?",
            "difficulty": "advanced",
            "options": [
                "Lightweight user-mode threads managed by the JVM rather than the OS kernel, enabling millions of concurrent threads",
                "Threads executing on external cloud instances",
                "Simulated threads for running unit tests without CPU",
                "Threads that can only perform synchronous file writes"
            ],
            "correct_answer": "Lightweight user-mode threads managed by the JVM rather than the OS kernel, enabling millions of concurrent threads",
            "explanation": "Virtual threads are lightweight threads decoupled from OS threads, dramatically simplifying high-throughput concurrent code."
        },
        {
            "question": "In Hibernate/JPA, what is the N+1 SELECT problem and how is it resolved?",
            "difficulty": "advanced",
            "options": [
                "Executing 1 query for parent entities and N subsequent queries for children; resolved using JOIN FETCH or entity graphs",
                "A bug where 1 transaction fails N times",
                "When a table has N+1 foreign keys",
                "A memory leak caused by unclosed statements"
            ],
            "correct_answer": "Executing 1 query for parent entities and N subsequent queries for children; resolved using JOIN FETCH or entity graphs",
            "explanation": "N+1 query problem occurs when lazy relations trigger individual queries per row, solved via eager join fetches."
        },
        {
            "question": "What is Escape Analysis performed by the JVM JIT compiler?",
            "difficulty": "advanced",
            "options": [
                "Determining if an object is accessible outside the current method/thread, allowing stack allocation and lock elimination",
                "Escaping SQL injection strings automatically",
                "Preventing memory overflow in long loops",
                "Escaping recursive stack overflows"
            ],
            "correct_answer": "Determining if an object is accessible outside the current method/thread, allowing stack allocation and lock elimination",
            "explanation": "If an object does not escape a method, the JIT can allocate it on the stack rather than the heap and elide synchronization."
        }
    ],

    "cloud_devops": [
        # Beginner
        {
            "question": "What is the fundamental difference between Docker and a traditional Virtual Machine?",
            "difficulty": "beginner",
            "options": [
                "Docker containers share the host OS kernel and are lightweight; VMs run full guest operating systems on a hypervisor",
                "VMs share the host kernel while Docker runs full guest OS",
                "Docker can only run on Linux",
                "VMs do not use CPU resources"
            ],
            "correct_answer": "Docker containers share the host OS kernel and are lightweight; VMs run full guest operating systems on a hypervisor",
            "explanation": "Containers virtualize at the OS level sharing the kernel, while VMs virtualize hardware via hypervisors."
        },
        {
            "question": "In Kubernetes, what is the smallest deployable computing unit?",
            "difficulty": "beginner",
            "options": ["Pod", "Node", "Cluster", "Deployment"],
            "correct_answer": "Pod",
            "explanation": "A Pod encapsulates one or more containers sharing storage and network specifications."
        },
        {
            "question": "What does CI/CD stand for in modern software engineering?",
            "difficulty": "beginner",
            "options": [
                "Continuous Integration / Continuous Delivery (or Deployment)",
                "Central Intelligence / Central Database",
                "Code Inspection / Code Debugging",
                "Container Initialization / Container Destruction"
            ],
            "correct_answer": "Continuous Integration / Continuous Delivery (or Deployment)",
            "explanation": "CI/CD automates building, testing, and releasing code changes rapidly and reliably."
        },
        {
            "question": "Which AWS service provides resizable, on-demand compute capacity in the cloud?",
            "difficulty": "beginner",
            "options": ["Amazon EC2", "Amazon S3", "Amazon RDS", "Amazon SQS"],
            "correct_answer": "Amazon EC2",
            "explanation": "Amazon Elastic Compute Cloud (EC2) provides scalable virtual servers in AWS."
        },
        {
            "question": "What is Dockerfile in container workflows?",
            "difficulty": "beginner",
            "options": [
                "A text document containing commands to assemble a Docker image",
                "A running container instance",
                "A cloud registry for hosting images",
                "A Kubernetes configuration manifest"
            ],
            "correct_answer": "A text document containing commands to assemble a Docker image",
            "explanation": "Dockerfile defines step-by-step instructions to build a container image."
        },
        {
            "question": "What is Infrastructure as Code (IaC)?",
            "difficulty": "beginner",
            "options": [
                "Managing and provisioning computing infrastructure through machine-readable definition files (e.g. Terraform)",
                "Writing application code directly inside cloud consoles",
                "Converting backend APIs to assembly code",
                "Running automated unit tests in Python"
            ],
            "correct_answer": "Managing and provisioning computing infrastructure through machine-readable definition files (e.g. Terraform)",
            "explanation": "IaC defines and manages servers, networks, and storage using declarative code repositories."
        },
        # Intermediate
        {
            "question": "In Kubernetes, what is the role of a Service resource?",
            "difficulty": "intermediate",
            "options": [
                "An abstraction that defines a logical set of Pods and a persistent network access policy / IP",
                "A script that runs backups on a cron schedule",
                "A physical worker machine in the cloud",
                "A container image registry"
            ],
            "correct_answer": "An abstraction that defines a logical set of Pods and a persistent network access policy / IP",
            "explanation": "Kubernetes Services provide stable IP addresses and DNS names to route traffic to dynamic pods."
        },
        {
            "question": "What is the difference between Docker multi-stage builds and single-stage builds?",
            "difficulty": "intermediate",
            "options": [
                "Multi-stage builds leave behind build tools and compilers, yielding drastically smaller and more secure production images",
                "Single-stage builds are faster and more secure",
                "Multi-stage builds can only be used on Windows",
                "Multi-stage builds run containers across multiple clouds"
            ],
            "correct_answer": "Multi-stage builds leave behind build tools and compilers, yielding drastically smaller and more secure production images",
            "explanation": "Multi-stage builds selectively copy artifacts from earlier build stages, minimizing the final image size."
        },
        {
            "question": "In AWS, what is the purpose of an IAM Role?",
            "difficulty": "intermediate",
            "options": [
                "An identity with permission policies that can be assumed by applications, services, or users without hardcoded credentials",
                "A billing tier for enterprise customers",
                "A physical hardware security module",
                "A database user account in RDS"
            ],
            "correct_answer": "An identity with permission policies that can be assumed by applications, services, or users without hardcoded credentials",
            "explanation": "IAM roles provide temporary security credentials to AWS services and instances securely."
        },
        {
            "question": "What is the primary function of a reverse proxy like Nginx in microservices?",
            "difficulty": "intermediate",
            "options": [
                "Load balancing, SSL termination, caching, and routing requests to upstream backend services",
                "Compiling front-end React code on the fly",
                "Storing user passwords in memory",
                "Generating automated unit test reports"
            ],
            "correct_answer": "Load balancing, SSL termination, caching, and routing requests to upstream backend services",
            "explanation": "Reverse proxies sit between clients and servers, providing security, caching, SSL, and load balancing."
        },
        {
            "question": "What is Canary Deployment in release management?",
            "difficulty": "intermediate",
            "options": [
                "Rolling out a new version to a small subset of users before making it available to the entire infrastructure",
                "Switching 100% of traffic instantaneously between two identical environments",
                "Stopping all servers while uploading new code",
                "Deploying only bug fixes on weekends"
            ],
            "correct_answer": "Rolling out a new version to a small subset of users before making it available to the entire infrastructure",
            "explanation": "Canary releases test stability on a small percentage of real production traffic before full deployment."
        },
        {
            "question": "What is a ConfigMap in Kubernetes?",
            "difficulty": "intermediate",
            "options": [
                "An API object used to store non-confidential configuration data in key-value pairs consumed by Pods",
                "A secret vault for storing private SSH keys",
                "A map of physical server locations in the datacenter",
                "A network topology visualizer"
            ],
            "correct_answer": "An API object used to store non-confidential configuration data in key-value pairs consumed by Pods",
            "explanation": "ConfigMaps decouple configuration artifacts from container image content for portability."
        },
        {
            "question": "What is the role of Prometheus and Grafana in modern infrastructure?",
            "difficulty": "intermediate",
            "options": [
                "Prometheus scrapes and stores time-series metrics; Grafana visualizes and dashboards them",
                "Prometheus compiles Docker images; Grafana deploys them to AWS",
                "Prometheus manages DNS records; Grafana provides CDN caching",
                "Prometheus handles user authentication; Grafana hashes passwords"
            ],
            "correct_answer": "Prometheus scrapes and stores time-series metrics; Grafana visualizes and dashboards them",
            "explanation": "Prometheus is a time-series monitoring system, while Grafana renders interactive visual dashboards."
        },
        # Advanced
        {
            "question": "In Kubernetes, what are CNI (Container Network Interface) plugins responsible for?",
            "difficulty": "advanced",
            "options": [
                "Configuring network interfaces, assigning IP addresses to Pods, and enabling inter-pod communication across nodes",
                "Managing persistent disk storage volume attachments",
                "Authenticating kubectl user requests with LDAP",
                "Compiling container source code inside nodes"
            ],
            "correct_answer": "Configuring network interfaces, assigning IP addresses to Pods, and enabling inter-pod communication across nodes",
            "explanation": "CNI plugins (Calico, Flannel, Cilium) allocate pod IP addresses and route overlay network traffic across nodes."
        },
        {
            "question": "What is the Raft Consensus Algorithm in distributed systems like etcd (Kubernetes control plane)?",
            "difficulty": "advanced",
            "options": [
                "A consensus algorithm that elects a leader and replicates a log of state machine transitions across an odd quorum of nodes",
                "A load balancing hashing algorithm for HTTP requests",
                "A memory compaction algorithm in the Linux kernel",
                "A cryptographic hashing function replacing SHA-256"
            ],
            "correct_answer": "A consensus algorithm that elects a leader and replicates a log of state machine transitions across an odd quorum of nodes",
            "explanation": "etcd uses Raft to maintain consistent, fault-tolerant state for the entire Kubernetes cluster."
        },
        {
            "question": "What is a Service Mesh (such as Istio or Linkerd) in cloud microservices?",
            "difficulty": "advanced",
            "options": [
                "A dedicated infrastructure layer using sidecar proxies to manage service-to-service communication, mTLS encryption, and observability",
                "A physical mesh of fiber optic cables in AWS datacenters",
                "A distributed database engine replacing PostgreSQL",
                "A web framework for building REST APIs"
            ],
            "correct_answer": "A dedicated infrastructure layer using sidecar proxies to manage service-to-service communication, mTLS encryption, and observability",
            "explanation": "Service meshes deploy Envoy sidecars alongside containers to automate mTLS, tracing, retries, and circuit breaking."
        },
        {
            "question": "What is the CAP Theorem in distributed data systems?",
            "difficulty": "advanced",
            "options": [
                "A distributed system can guarantee at most two of: Consistency, Availability, and Partition Tolerance",
                "Computers, Access, and Performance must all be maximized",
                "CPU, Architecture, and RAM determine system throughput",
                "Containers, Applications, and Platforms must share one runtime"
            ],
            "correct_answer": "A distributed system can guarantee at most two of: Consistency, Availability, and Partition Tolerance",
            "explanation": "In the presence of network partitions (P), a distributed system must trade off between consistency (C) and availability (A)."
        },
        {
            "question": "How does Linux cgroups (control groups) work with namespaces to isolate Docker containers?",
            "difficulty": "advanced",
            "options": [
                "Namespaces isolate what a container can see (PID, NET, MNT); cgroups limit how much resources (CPU, RAM, I/O) it can use",
                "cgroups isolate process IDs while namespaces manage CPU clock cycles",
                "Namespaces compile bytecode; cgroups allocate disk sectors",
                "They are deprecated features replaced by virtual machines"
            ],
            "correct_answer": "Namespaces isolate what a container can see (PID, NET, MNT); cgroups limit how much resources (CPU, RAM, I/O) it can use",
            "explanation": "Namespaces provide isolation (processes, networks, mounts); cgroups enforce resource consumption limits."
        },
        {
            "question": "What is GitOps (e.g. ArgoCD or Flux) in continuous delivery?",
            "difficulty": "advanced",
            "options": [
                "Using Git repositories as the single source of truth for declarative infrastructure and applications, reconciled automatically by agents",
                "Running git commit automatically on every keyboard keystroke",
                "A project management methodology replacing Agile",
                "A cloud hosting provider for git remotes"
            ],
            "correct_answer": "Using Git repositories as the single source of truth for declarative infrastructure and applications, reconciled automatically by agents",
            "explanation": "GitOps ensures the cluster state matches the declarative definitions stored in git through automated reconciliation."
        },
        {
            "question": "What is the purpose of Kubernetes Horizontal Pod Autoscaler (HPA)?",
            "difficulty": "advanced",
            "options": [
                "Automatically scales the number of Pod replicas up or down based on observed CPU, memory, or custom metrics",
                "Increases the physical CPU clock frequency of worker nodes",
                "Backs up container files to Amazon S3",
                "Rotates SSL certificates automatically"
            ],
            "correct_answer": "Automatically scales the number of Pod replicas up or down based on observed CPU, memory, or custom metrics",
            "explanation": "HPA adjusts deployment replica counts dynamically in response to workload traffic spikes."
        }
    ]
}
