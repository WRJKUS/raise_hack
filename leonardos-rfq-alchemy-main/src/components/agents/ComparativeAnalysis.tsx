
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, Star, DollarSign, Mail, Building, Calendar } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient, AnalysisResult } from '@/lib/api';

const ComparativeAnalysis = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const { toast } = useToast();

  // Load analysis results on component mount
  useEffect(() => {
    loadAnalysisResults();
    testBackendConnection();
  }, []);

  const testBackendConnection = async () => {
    try {
      console.log('Testing backend connection...');

      // Test direct fetch first
      console.log('Testing direct fetch to 127.0.0.1:8000...');
      const directResponse = await fetch('http://127.0.0.1:8000/api/health');
      console.log('Direct fetch response status:', directResponse.status);
      const directData = await directResponse.json();
      console.log('Direct fetch data:', directData);

      // Test through API client
      const health = await apiClient.healthCheck();
      console.log('Backend connection successful:', health);
    } catch (error) {
      console.error('Backend connection failed:', error);
      toast({
        title: "Backend Connection Issue",
        description: "Cannot connect to the backend server. Make sure it's running on port 8000.",
        variant: "destructive"
      });
    }
  };

  const loadAnalysisResults = async (sessionId?: string) => {
    try {
      const results = await apiClient.getAnalysisResults(sessionId || currentSessionId);
      setAnalysisResults(results);
      console.log(`Loaded ${results.length} analysis results${sessionId ? ` for session ${sessionId}` : ''}`);
    } catch (error) {
      console.error('Failed to load analysis results:', error);
      // Don't show error toast on initial load if no results exist
    }
  };

  const handleFileUpload = async (event) => {
    console.log('File input changed, event:', event);
    const files = Array.from(event.target.files) as File[];
    console.log('Selected files:', files);

    if (files.length === 0) {
      console.log('No files selected');
      return;
    }

    console.log(`Starting upload of ${files.length} file(s)`);
    setIsUploading(true);
    const uploadedFileData = [];

    try {
      for (const file of files) {
        console.log(`Uploading file: ${file.name} (${file.size} bytes)`);
        try {
          const result = await apiClient.uploadProposal(file);
          console.log(`Upload successful for ${file.name}:`, result);
          uploadedFileData.push({
            id: result.file_id,
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: new Date(),
            status: 'uploaded'
          });
        } catch (error) {
          console.error(`Failed to upload ${file.name}:`, error);
          uploadedFileData.push({
            id: Date.now() + Math.random(),
            name: file.name,
            size: file.size,
            type: file.type,
            uploadedAt: new Date(),
            status: 'error',
            error: error.message
          });
        }
      }

      setUploadedFiles(prev => [...prev, ...uploadedFileData]);

      const successCount = uploadedFileData.filter(f => f.status === 'uploaded').length;
      const errorCount = uploadedFileData.filter(f => f.status === 'error').length;

      if (successCount > 0) {
        toast({
          title: "Files uploaded successfully",
          description: `${successCount} proposal(s) ready for analysis${errorCount > 0 ? `, ${errorCount} failed` : ''}`,
        });
      }

      if (errorCount > 0 && successCount === 0) {
        toast({
          title: "Upload failed",
          description: `Failed to upload ${errorCount} file(s)`,
          variant: "destructive"
        });
      }
    } finally {
      console.log('Upload process completed, setting isUploading to false');
      setIsUploading(false);
    }
  };

  const startAnalysis = async () => {
    const uploadedCount = uploadedFiles.filter(f => f.status === 'uploaded').length;
    if (uploadedCount === 0) {
      toast({
        title: "No files to analyze",
        description: "Please upload some proposals first",
        variant: "destructive"
      });
      return;
    }

    setIsAnalyzing(true);

    try {
      // Start the analysis workflow
      const analysisResponse = await apiClient.startAnalysis();
      const sessionId = analysisResponse.session_id;

      // Store the session ID for future requests
      setCurrentSessionId(sessionId);

      console.log(`Analysis started with session ID: ${sessionId}`);

      // Load the updated analysis results with the session ID
      await loadAnalysisResults(sessionId);

      toast({
        title: "Analysis completed",
        description: "All proposals have been analyzed and scored using AI",
      });
    } catch (error) {
      console.error('Analysis failed:', error);
      toast({
        title: "Analysis failed",
        description: error.message || "Failed to analyze proposals",
        variant: "destructive"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadgeVariant = (score) => {
    if (score >= 90) return 'default';
    if (score >= 75) return 'secondary';
    return 'destructive';
  };

  return (
    <div className="space-y-6">
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Agent 1: Comparative Analysis
          </CardTitle>
          <CardDescription>
            Upload PDF proposals for intelligent analysis against your existing RFP portfolio
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Upload Section */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors">
            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Proposal Documents</h3>
            <p className="text-gray-600 mb-4">Drop your PDF files here or click to browse</p>
            <input
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
            />
            <Button asChild className="bg-blue-600 hover:bg-blue-700">
              <label htmlFor="file-upload" className="cursor-pointer">
                Choose Files
              </label>
            </Button>
          </div>

          {/* Uploaded Files */}
          {uploadedFiles.length > 0 && (
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Uploaded Files ({uploadedFiles.length})</h4>
              {uploadedFiles.map((file) => (
                <div key={file.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-red-600" />
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-600">
                        {(file.size / 1024 / 1024).toFixed(2)} MB • Uploaded {file.uploadedAt.toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <Badge variant={file.status === 'uploaded' ? 'default' : file.status === 'error' ? 'destructive' : 'outline'}>
                    {file.status === 'uploaded' ? 'Ready' : file.status === 'error' ? 'Error' : 'Processing'}
                  </Badge>
                </div>
              ))}
            </div>
          )}

          {/* Analysis Controls */}
          <div className="flex items-center gap-4">
            <div className="flex gap-2">
              <Button
                onClick={startAnalysis}
                disabled={isAnalyzing || isUploading || uploadedFiles.filter(f => f.status === 'uploaded').length === 0}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {isAnalyzing ? 'Analyzing...' : isUploading ? 'Uploading...' : 'Start AI Analysis'}
              </Button>
              {isUploading && (
                <Button
                  onClick={() => {
                    console.log('Manual reset of upload state');
                    setIsUploading(false);
                  }}
                  variant="outline"
                  className="text-red-600 border-red-600"
                >
                  Reset Upload
                </Button>
              )}
            </div>
            {isAnalyzing && (
              <div className="flex-1 max-w-md">
                <p className="text-sm text-gray-600 mb-2">Analyzing proposals...</p>
                <Progress value={75} className="w-full" />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResults.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900">Analysis Results</h3>

          {analysisResults.map((result) => (
            <Card key={result.id} className="bg-white shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Building className="w-5 h-5" />
                    {result.vendor}
                  </CardTitle>
                  <Badge variant={getScoreBadgeVariant(result.overallScore)} className="text-lg px-3 py-1">
                    {result.overallScore}/100
                  </Badge>
                </div>
                <CardDescription>{result.fileName}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Score Breakdown */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Technical Score</span>
                      <span className={`font-bold ${getScoreColor(result.technicalScore)}`}>
                        {result.technicalScore}%
                      </span>
                    </div>
                    <Progress value={result.technicalScore} className="w-full" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Budget Score</span>
                      <span className={`font-bold ${getScoreColor(result.budgetScore)}`}>
                        {result.budgetScore}%
                      </span>
                    </div>
                    <Progress value={result.budgetScore} className="w-full" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Timeline Score</span>
                      <span className={`font-bold ${getScoreColor(result.timelineScore)}`}>
                        {result.timelineScore}%
                      </span>
                    </div>
                    <Progress value={result.timelineScore} className="w-full" />
                  </div>
                </div>

                {/* Key Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-green-600" />
                    <div>
                      <p className="text-xs text-gray-600">Proposed Budget</p>
                      <p className="font-semibold">{result.proposedBudget}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-blue-600" />
                    <div>
                      <p className="text-xs text-gray-600">Timeline</p>
                      <p className="font-semibold">{result.timeline}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-purple-600" />
                    <div>
                      <p className="text-xs text-gray-600">Contact Email</p>
                      <p className="font-semibold text-sm">{result.contact}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <Building className="w-4 h-4 text-orange-600" />
                    <div>
                      <p className="text-xs text-gray-600">Phone</p>
                      <p className="font-semibold text-sm">{result.phone}</p>
                    </div>
                  </div>
                </div>

                {/* Strengths and Concerns */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-green-800 mb-3 flex items-center gap-2">
                      <Star className="w-4 h-4" />
                      Key Strengths
                    </h4>
                    <ul className="space-y-2">
                      {result.strengths.map((strength, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-sm text-gray-700">{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h4 className="font-medium text-red-800 mb-3 flex items-center gap-2">
                      <Star className="w-4 h-4" />
                      Areas of Concern
                    </h4>
                    <ul className="space-y-2">
                      {result.concerns.map((concern, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0"></div>
                          <span className="text-sm text-gray-700">{concern}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default ComparativeAnalysis;
