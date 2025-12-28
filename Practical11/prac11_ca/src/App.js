import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './Navbar';
import Home from './Home';
import Enquire from './Enquire';
import ClientData from './ClientData';
import AdminLogin from './AdminLogin';
import AdminClientEntry from './AdminClientEntry';
import AdminEnquiries from './AdminEnquiries';
import AdminDashboard from './AdminDashboard';
import './App.css';
import Careers from './Careers';
import AdminApplications from './AdminApplications';
import AdminAddJob from './AdminAddJob';


function App() {
  return (
    <BrowserRouter>
      <Navbar /> 
      <Routes>
        <Route path="/admin/jobs/add" element={<AdminAddJob />} />
        <Route path="/" element={<Home />} />
        <Route path="/enquire" element={<Enquire />} />
        <Route path="/clients" element={<ClientData />} />
        <Route path="/admin" element={<AdminLogin />} />
        <Route path="/admin/client" element={<AdminClientEntry />} />
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/enquiries" element={<AdminEnquiries />} />
        <Route path="/careers" element={<Careers />} />
        <Route path="/admin/applications" element={<AdminApplications />} />
      </Routes>
    </BrowserRouter>
  );
}


export default App;
