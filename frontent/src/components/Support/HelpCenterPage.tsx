import React from 'react';

const HelpCenterPage: React.FC = () => {
  const email = 'helptrylo@gmail.com';
  const mailto = `mailto:${email}?subject=Support%20Request&body=Hello%20Trylo%20Support,%0D%0A%0D%0A`;
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8 max-w-lg w-full">
        <h1 className="text-2xl font-semibold text-gray-900 mb-4">Help Center</h1>
        <p className="text-gray-700 mb-2">For any enquiries, contact us at:</p>
        <a href={mailto} className="text-amber-700 underline">{email}</a>
        <div className="mt-6">
          <button
            onClick={() => window.open(mailto, '_self')}
            className="px-5 py-3 bg-amber-600 text-white rounded-md hover:bg-amber-700"
          >
            Complaint / Email Support
          </button>
        </div>
      </div>
    </div>
  );
};

export default HelpCenterPage;


