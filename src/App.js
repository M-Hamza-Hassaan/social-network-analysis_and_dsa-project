import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, History, Settings, Github, BarChart2 } from 'lucide-react';

// Custom Card Component
const Card = ({ children, className }) => (
  <div className={`bg-white shadow-lg rounded-lg p-4 ${className}`}>{children}</div>
);

const CardHeader = ({ children }) => <div className="mb-4 border-b pb-2">{children}</div>;
const CardTitle = ({ children }) => <h2 className="text-lg font-semibold">{children}</h2>;
const CardContent = ({ children }) => <div>{children}</div>;

// Navigation Component
const Navigation = () => {
  const location = useLocation();
  
  const navItems = [
    { path: '/', name: 'Home', icon: Home },
    { path: '/dashboard', name: 'Dashboard', icon: BarChart2 },
    { path: '/history', name: 'History', icon: History },
    { path: '/settings', name: 'Settings', icon: Settings }
  ];

  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex space-x-8">
          {navItems.map(({ path, name, icon: Icon }) => (
            <Link
              key={path}
              to={path}
              className={`py-4 px-3 flex items-center space-x-2
                ${location.pathname === path 
                  ? 'border-b-2 border-blue-500 text-blue-600' 
                  : 'text-gray-600 hover:text-gray-900'}`}
            >
              <Icon className="w-5 h-5" />
              <span>{name}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

// Home Page Component
const HomePage = () => {
  const [prUrl, setPrUrl] = React.useState('');
  const [isAnalyzing, setIsAnalyzing] = React.useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setTimeout(() => setIsAnalyzing(false), 2000);
  };

  return (
    <div className="space-y-8 bg-gray-100 min-h-screen flex flex-col items-center justify-center p-6">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-navy-900">AI Code Reviewer</h1>
        <p className="text-gray-700">Get instant, intelligent feedback on your pull requests</p>
      </div>

      <Card className="bg-white shadow-lg rounded-lg w-full max-w-lg border border-gray-200">
        <CardHeader className="bg-navy-600 text-white p-4 rounded-t-lg">
          <CardTitle className="flex items-center gap-2 text-lg font-semibold">
            <Github className="w-6 h-6" />
            Submit Pull Request
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <input
              type="url"
              placeholder="Enter GitHub PR URL"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-navy-500 border-gray-300"
              value={prUrl}
              onChange={(e) => setPrUrl(e.target.value)}
              required
            />
            <button
              type="submit"
              className={`w-full py-3 px-4 rounded-lg text-white font-medium transition 
                ${isAnalyzing ? 'bg-navy-400' : 'bg-navy-600 hover:bg-navy-700'}`}
              disabled={isAnalyzing}
            >
              {isAnalyzing ? 'Analyzing...' : 'Review Code'}
            </button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};


// Dashboard Page Component
const DashboardPage = () => (
  <div className="space-y-6">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {[
        { title: 'Total Reviews', value: '156', trend: '+12%' },
        { title: 'Avg. Score', value: '85/100', trend: '+5%' },
        { title: 'Issues Found', value: '1,234', trend: '-8%' }
      ].map((stat, index) => (
        <Card key={index}>
          <CardContent className="pt-6">
            <p className="text-gray-600">{stat.title}</p>
            <div className="flex items-end justify-between mt-2">
              <p className="text-2xl font-bold">{stat.value}</p>
              <span className={`text-sm ${
                stat.trend.startsWith('+') ? 'text-green-500' : 'text-red-500'
              }`}>{stat.trend}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>

    <Card>
      <CardHeader>
        <CardTitle>Recent Reviews</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {[
            { repo: 'frontend-app', score: 92, issues: 3, status: 'passed' },
            { repo: 'api-service', score: 78, issues: 8, status: 'failed' },
            { repo: 'utils', score: 95, issues: 1, status: 'passed' }
          ].map((review, index) => (
            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
              <div className="flex items-center space-x-4">
                <Github className="w-5 h-5" />
                <span className="font-medium">{review.repo}</span>
              </div>
              <div className="flex items-center space-x-8">
                <span>Score: {review.score}</span>
                <span>Issues: {review.issues}</span>
                <span className={`text-sm ${
                  review.status === 'passed' ? 'text-green-500' : 'text-red-500'
                }`}>
                  {review.status.toUpperCase()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

// History Page Component
const HistoryPage = () => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle>Review History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {[...Array(5)].map((_, index) => (
            <div key={index} className="p-4 border rounded-lg space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Github className="w-5 h-5" />
                  <span className="font-medium">Repository {index + 1}</span>
                </div>
                <span className="text-sm text-gray-500">2 days ago</span>
              </div>
              <div className="flex items-center justify-between text-sm text-gray-600">
                <span>PR #123: Feature implementation</span>
                <span>Score: 88/100</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

// Settings Page Component
const SettingsPage = () => (
  <div className="space-y-6">
    <Card>
      <CardHeader>
        <CardTitle>GitHub Integration</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 border rounded-lg">
            <div className="flex items-center space-x-4">
              <Github className="w-5 h-5" />
              <span>Connected to GitHub</span>
            </div>
            <button className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg">
              Disconnect
            </button>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>Review Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {[
            'Automatically review new PRs',
            'Send Slack notifications',
            'Include security analysis',
            'Generate fix suggestions'
          ].map((setting, index) => (
            <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
              <span>{setting}</span>
              <div className="w-12 h-6 bg-blue-600 rounded-full relative cursor-pointer">
                <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full"></div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  </div>
);

// Main App Component
const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
        <Navigation />
        <main className="max-w-7xl mx-auto p-6">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;
