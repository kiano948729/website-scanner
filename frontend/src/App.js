import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Businesses from './pages/Businesses';
import Jobs from './pages/Jobs';
import WebsiteChecks from './pages/WebsiteChecks';
import Exports from './pages/Exports';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/businesses" element={<Businesses />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/website-checks" element={<WebsiteChecks />} />
          <Route path="/exports" element={<Exports />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
