import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import LiveView from './pages/LiveView';
import Training from './pages/Training';
import Cameras from './pages/Cameras';
import Analytics from './pages/Analytics';



function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/live" element={<LiveView />} />
          <Route path="/training" element={<Training />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/cameras" element={<Cameras />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
