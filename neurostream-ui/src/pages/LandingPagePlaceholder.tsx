import React from 'react';
import Button from '../ui/Button';
import Card from '../ui/Card';

const LandingPagePlaceholder: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-4 space-y-12">
      {/* Hero Section */}
      <section className="text-center py-16 space-y-4">
        <h1 className="text-5xl font-bold text-cyan-400">NeuroStream</h1>
        <p className="text-xl text-gray-300">
          AI-Powered Neuroscience Research Tools
        </p>
        <Button>Get Started</Button>
      </section>

      {/* Feature Cards Section */}
      <section className="w-full max-w-4xl">
        <h2 className="text-3xl font-semibold text-center mb-8 text-gray-100">
          Features
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          <Card title="Literature Engine">
            <p className="text-gray-400">
              Discover relevant papers and insights from millions of publications.
            </p>
          </Card>
          <Card title="Protocol Generator">
            <p className="text-gray-400">
              Generate and optimize research protocols with AI assistance.
            </p>
          </Card>
          <Card title="Analytics Suite">
            <p className="text-gray-400">
              Analyze your data and visualize complex findings effortlessly.
            </p>
          </Card>
        </div>
      </section>
    </div>
  );
};

export default LandingPagePlaceholder;
