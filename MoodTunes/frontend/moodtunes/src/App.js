import {useState} from React;
// import './App.css';

function App() {
  const [username, setUsername] = useState("")
  const [genres, setGenres] = useState([])
  const [message, setMessage] = useState("")

  const handleSubmit = async () => {
    const response = await fetch("http://localhost:5000/create-user", {
      method : "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({username, genres})
  });
  
  const data = await response.json();
  setMessage(data.message || data.error);
}
  return (
    <div className="main">
        
    </div>
    );
}

export default App;
