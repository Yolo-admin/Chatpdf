
import FileUpload from './components/FileUpload';
import ChatWindow from './components/ChatWindow';
import './App.css';

function App() {
  
  return (
    <div className="app-container">
      <div className="header">PDFChat</div>
      <FileUpload />
      <ChatWindow />
    </div>
  );
}

export default App;
