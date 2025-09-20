'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/hooks/useUser';

interface Institution {
  institution_id: string;
  institution_name: string;
  region: string;
  student_count: number;
  active: boolean;
}

const REGIONS = [
  'North India',
  'South India', 
  'East India',
  'West India',
  'Central India',
  'Northeast India'
];

const LANGUAGES = [
  { code: 'en-US', name: 'English' },
  { code: 'hi-IN', name: 'Hindi' },
  { code: 'ta-IN', name: 'Tamil' },
  { code: 'te-IN', name: 'Telugu' },
  { code: 'bn-IN', name: 'Bengali' },
  { code: 'mr-IN', name: 'Marathi' },
  { code: 'gu-IN', name: 'Gujarati' },
  { code: 'kn-IN', name: 'Kannada' },
  { code: 'ml-IN', name: 'Malayalam' },
  { code: 'pa-IN', name: 'Punjabi' }
];

interface OnboardingFormData {
  role: 'student' | 'institution';
  profile: Record<string, string>;
  institution_id?: string;
}

export default function OnboardingPage() {
  const router = useRouter();
  const { user, loading } = useUser();
  
  const [formData, setFormData] = useState<OnboardingFormData>({
    role: 'student',
    profile: {}
  });
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loadingInstitutions, setLoadingInstitutions] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect if user is not authenticated or already onboarded
  useEffect(() => {
    if (!loading && !user) {
      router.push('/');
      return;
    }
    
    if (!loading && user && user.onboarding_completed) {
      router.push('/');
      return;
    }
  }, [user, loading, router]);

  // Fetch institutions on component mount since default role is student
  useEffect(() => {
    if (!loading && user) {
      fetchInstitutions();
    }
  }, [loading, user]);

  // Fetch institutions for student role
  const fetchInstitutions = async () => {
    setLoadingInstitutions(true);
    try {
      const response = await fetch('/api/v1/users/institutions', {
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setInstitutions(data.institutions || []);
      } else {
        console.error('Failed to fetch institutions. Status:', response.status);
        setInstitutions([]);
      }
    } catch (error) {
      console.error('Error fetching institutions:', error);
      setInstitutions([]);
    } finally {
      setLoadingInstitutions(false);
    }
  };

  const handleRoleChange = (role: 'student' | 'institution') => {
    setFormData({
      role,
      profile: {}, // Reset profile when role changes
      institution_id: undefined // Reset institution selection
    });

    // Fetch institutions when student role is selected
    if (role === 'student' && institutions.length === 0) {
      fetchInstitutions();
    }
  };

  const handleProfileChange = (key: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      profile: {
        ...prev.profile,
        [key]: value
      }
    }));
  };

  const validateForm = (): boolean => {
    if (formData.role === 'student') {
      const required = ['name', 'age', 'region', 'language_preference'];
      const profileValid = required.every(field => formData.profile[field]?.trim());
      // Institution selection is optional (can be "No Institution")
      return profileValid;
    } else {
      const required = ['institution_name', 'contact_person', 'region'];
      return required.every(field => formData.profile[field]?.trim());
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      setError('Please fill in all required fields.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/users/onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to complete onboarding');
      }

      // Redirect to main app
      router.push('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show loading while checking auth status
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-300 border-t-indigo-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to MITRA
          </h1>
          <p className="text-gray-600">
            Let's personalize your experience. Please tell us about yourself.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              I am a:
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => handleRoleChange('student')}
                className={`p-3 rounded-lg border-2 text-sm font-medium transition-colors ${
                  formData.role === 'student'
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                Student
              </button>
              <button
                type="button"
                onClick={() => handleRoleChange('institution')}
                className={`p-3 rounded-lg border-2 text-sm font-medium transition-colors ${
                  formData.role === 'institution'
                    ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
                    : 'border-gray-300 bg-white text-gray-700 hover:border-gray-400'
                }`}
              >
                Institution
              </button>
            </div>
          </div>

          {/* Student Fields */}
          {formData.role === 'student' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  value={formData.profile.name || ''}
                  onChange={(e) => handleProfileChange('name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter your full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Age *
                </label>
                <input
                  type="number"
                  min="13"
                  max="100"
                  value={formData.profile.age || ''}
                  onChange={(e) => handleProfileChange('age', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter your age"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Region *
                </label>
                <select
                  value={formData.profile.region || ''}
                  onChange={(e) => handleProfileChange('region', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Select your region</option>
                  {REGIONS.map((region) => (
                    <option key={region} value={region}>
                      {region}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Preferred Language *
                </label>
                <select
                  value={formData.profile.language_preference || ''}
                  onChange={(e) => handleProfileChange('language_preference', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Select your preferred language</option>
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Institution (Optional)
                </label>
                {loadingInstitutions ? (
                  <div className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500">
                    Loading institutions...
                  </div>
                ) : (
                  <select
                    value={formData.institution_id || ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      institution_id: e.target.value || undefined
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option value="">No Institution</option>
                    {institutions.length === 0 ? (
                      <option value="" disabled>No institutions available</option>
                    ) : (
                      institutions.map((institution) => (
                        <option key={institution.institution_id} value={institution.institution_id}>
                          {institution.institution_name} ({institution.region})
                        </option>
                      ))
                    )}
                  </select>
                )}
                <p className="text-xs text-gray-500 mt-1">
                  Select your institution if it's listed, or choose "No Institution" if not available.
                </p>
              </div>
            </div>
          )}

          {/* Institution Fields */}
          {formData.role === 'institution' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Institution Name *
                </label>
                <input
                  type="text"
                  value={formData.profile.institution_name || ''}
                  onChange={(e) => handleProfileChange('institution_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter institution name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Person *
                </label>
                <input
                  type="text"
                  value={formData.profile.contact_person || ''}
                  onChange={(e) => handleProfileChange('contact_person', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  placeholder="Enter contact person name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Region *
                </label>
                <select
                  value={formData.profile.region || ''}
                  onChange={(e) => handleProfileChange('region', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Select your region</option>
                  {REGIONS.map((region) => (
                    <option key={region} value={region}>
                      {region}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting || !validateForm()}
            className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSubmitting ? 'Setting up your profile...' : 'Complete Setup'}
          </button>
        </form>

        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Your information is secure and used only to personalize your MITRA experience.
          </p>
        </div>
      </div>
    </div>
  );
}
