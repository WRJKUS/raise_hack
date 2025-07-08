
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Upload, FileText, Star, DollarSign, Mail, Building, Calendar, CheckCircle, Target, AlertTriangle, AlertCircle, Info, TrendingDown, TrendingUp } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiClient, AnalysisResult, RFPMismatch, RFPAlignment } from '@/lib/api';

const ComparativeAnalysis = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  // RFP document upload state
  const [uploadedRFPId, setUploadedRFPId] = useState<string | null>(null);
  const [isUploadingRFP, setIsUploadingRFP] = useState(false);
  const [rfpDocumentInfo, setRfpDocumentInfo] = useState<{
    filename: string;
    title: string;
    file_size: number;
  } | null>(null);

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

  const handleRFPFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      toast({
        title: "Invalid file type",
        description: "Please select a PDF file for the RFP document",
        variant: "destructive"
      });
      return;
    }

    // Immediately upload the selected file
    setIsUploadingRFP(true);
    try {
      const result = await apiClient.uploadRFPDocument(file);
      setUploadedRFPId(result.rfp_document_id);
      setRfpDocumentInfo({
        filename: result.filename,
        title: result.title,
        file_size: result.file_size
      });

      toast({
        title: "RFP document uploaded successfully",
        description: `${result.filename} is ready to be used as baseline for comparative analysis`,
      });
    } catch (error) {
      console.error('RFP upload failed:', error);
      toast({
        title: "RFP upload failed",
        description: error.message || "Failed to upload RFP document",
        variant: "destructive"
      });
    } finally {
      setIsUploadingRFP(false);
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
      // Start the analysis workflow with RFP context if available
      const analysisResponse = await apiClient.startAnalysis(uploadedRFPId);
      const sessionId = analysisResponse.session_id;

      // Store the session ID for future requests
      setCurrentSessionId(sessionId);

      console.log(`Analysis started with session ID: ${sessionId}${uploadedRFPId ? ` and RFP context: ${uploadedRFPId}` : ''}`);

      // Load the updated analysis results with the session ID
      await loadAnalysisResults(sessionId);

      toast({
        title: "Analysis completed",
        description: `All proposals have been analyzed and scored using AI${uploadedRFPId ? ' against your uploaded RFP document' : ''}`,
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

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-orange-600" />;
      case 'medium':
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case 'low':
        return <Info className="w-4 h-4 text-blue-600" />;
      default:
        return <Info className="w-4 h-4 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'border-red-200 bg-red-50';
      case 'high':
        return 'border-orange-200 bg-orange-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      case 'low':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getAlignmentIcon = (score: number) => {
    if (score >= 80) return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (score >= 60) return <TrendingUp className="w-4 h-4 text-yellow-600" />;
    return <TrendingDown className="w-4 h-4 text-red-600" />;
  };

  const getAlignmentColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
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
          {/* RFP Document Upload Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              <h3 className="text-lg font-medium text-gray-900">Step 1: Upload RFP Document (Optional)</h3>
            </div>


            {!uploadedRFPId ? (
              <div className="border-2 border-dashed border-blue-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors bg-blue-50">
                <FileText className="w-10 h-10 text-blue-400 mx-auto mb-3" />
                <h4 className="text-md font-medium text-gray-900 mb-2">Upload RFP Document</h4>
                <p className="text-gray-600 mb-4 text-sm">Select your RFP PDF file to use as baseline for analysis</p>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleRFPFileSelect}
                  className="hidden"
                  id="rfp-file-upload"
                />
                <Button
                  asChild
                  disabled={isUploadingRFP}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <label htmlFor="rfp-file-upload" className="cursor-pointer">
                    {isUploadingRFP ? 'Uploading...' : 'Choose RFP File'}
                  </label>
                </Button>
              </div>
            ) : (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <div className="flex-1">
                    <p className="font-medium text-green-800">RFP Document Uploaded</p>
                    <p className="text-sm text-green-700">
                      {rfpDocumentInfo?.title} ({(rfpDocumentInfo?.file_size / 1024 / 1024).toFixed(2)} MB)
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setUploadedRFPId(null);
                      setRfpDocumentInfo(null);
                    }}
                    className="text-green-700 border-green-300 hover:bg-green-100"
                  >
                    Change RFP
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="border-t border-gray-200"></div>

          {/* Proposal Upload Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Upload className="w-5 h-5 text-gray-600" />
              <h3 className="text-lg font-medium text-gray-900">Step 2: Upload Proposal Documents</h3>
            </div>
            <p className="text-sm text-gray-600">
              Upload vendor proposal PDF files for comparative analysis{uploadedRFPId ? ' against your RFP document' : ''}.
            </p>
          </div>

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
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Target className="w-5 h-5 text-green-600" />
              <h3 className="text-lg font-medium text-gray-900">Step 3: Run Comparative Analysis</h3>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex gap-2">
                <Button
                  onClick={startAnalysis}
                  disabled={isAnalyzing || isUploading || isUploadingRFP || uploadedFiles.filter(f => f.status === 'uploaded').length === 0}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {isAnalyzing ? 'Analyzing...' : isUploading ? 'Uploading...' : isUploadingRFP ? 'Uploading RFP...' : 'Start AI Analysis'}
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
                  <p className="text-sm text-gray-600 mb-2">
                    Analyzing proposals{uploadedRFPId ? ' against your RFP document' : ' using general best practices'}...
                  </p>
                  <Progress value={75} className="w-full" />
                </div>
              )}
            </div>

            {uploadedRFPId && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-sm text-blue-800">
                  <strong>RFP Context:</strong> Analysis will compare proposals against your uploaded RFP document for more accurate scoring and recommendations.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResults.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900">Analysis Results</h3>

          {/* RFP Mismatch Summary */}
          {uploadedRFPId && analysisResults.some(result => result.rfp_alignment) && (
            <Card className="border-blue-200 bg-blue-50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-blue-900">
                  <FileText className="w-5 h-5" />
                  RFP Alignment Summary
                </CardTitle>
                <CardDescription className="text-blue-700">
                  Analysis based on your uploaded RFP document requirements
                </CardDescription>
              </CardHeader>
              <CardContent>
                {(() => {
                  const totalMismatches = analysisResults.reduce((total, result) =>
                    total + (result.rfp_alignment?.mismatches?.length || 0), 0);
                  const criticalMismatches = analysisResults.reduce((total, result) =>
                    total + (result.rfp_alignment?.mismatches?.filter(m => m.severity === 'critical').length || 0), 0);
                  const highMismatches = analysisResults.reduce((total, result) =>
                    total + (result.rfp_alignment?.mismatches?.filter(m => m.severity === 'high').length || 0), 0);
                  const avgAlignment = Math.round(analysisResults.reduce((total, result) =>
                    total + (result.rfp_alignment?.overall_alignment_score || 0), 0) / analysisResults.length);

                  return (
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="text-center p-3 bg-white rounded-lg border">
                          <div className={`font-bold text-2xl ${getAlignmentColor(avgAlignment)}`}>
                            {avgAlignment}%
                          </div>
                          <div className="text-sm text-gray-600">Avg. Alignment</div>
                        </div>
                        <div className="text-center p-3 bg-white rounded-lg border">
                          <div className="font-bold text-2xl text-gray-800">{totalMismatches}</div>
                          <div className="text-sm text-gray-600">Total Issues</div>
                        </div>
                        <div className="text-center p-3 bg-white rounded-lg border">
                          <div className="font-bold text-2xl text-red-600">{criticalMismatches}</div>
                          <div className="text-sm text-gray-600">Critical</div>
                        </div>
                        <div className="text-center p-3 bg-white rounded-lg border">
                          <div className="font-bold text-2xl text-orange-600">{highMismatches}</div>
                          <div className="text-sm text-gray-600">High Priority</div>
                        </div>
                      </div>

                      {(criticalMismatches > 0 || highMismatches > 0) && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="w-5 h-5 text-yellow-600" />
                            <span className="font-medium text-yellow-800">Attention Required</span>
                          </div>
                          <p className="text-sm text-yellow-700">
                            {criticalMismatches > 0 && `${criticalMismatches} critical mismatch(es) detected. `}
                            {highMismatches > 0 && `${highMismatches} high-priority issue(s) identified. `}
                            Review individual proposals below for detailed alignment analysis.
                          </p>
                        </div>
                      )}
                    </div>
                  );
                })()}
              </CardContent>
            </Card>
          )}

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

                {/* RFP Alignment Analysis */}
                {result.rfp_alignment && uploadedRFPId && (
                  <div className="space-y-4">
                    <h4 className="font-medium text-blue-800 mb-3 flex items-center gap-2">
                      <FileText className="w-4 h-4" />
                      RFP Alignment Analysis
                    </h4>

                    {/* Overall Alignment Score */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-medium text-blue-900">Overall RFP Alignment</span>
                        <div className="flex items-center gap-2">
                          {getAlignmentIcon(result.rfp_alignment.overall_alignment_score)}
                          <span className={`font-bold ${getAlignmentColor(result.rfp_alignment.overall_alignment_score)}`}>
                            {result.rfp_alignment.overall_alignment_score}%
                          </span>
                        </div>
                      </div>
                      <Progress value={result.rfp_alignment.overall_alignment_score} className="w-full mb-2" />
                      <p className="text-sm text-blue-800">{result.rfp_alignment.alignment_summary}</p>
                    </div>

                    {/* Alignment Breakdown */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className={`font-bold text-lg ${getAlignmentColor(result.rfp_alignment.budget_alignment)}`}>
                          {result.rfp_alignment.budget_alignment}%
                        </div>
                        <div className="text-xs text-gray-600">Budget</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className={`font-bold text-lg ${getAlignmentColor(result.rfp_alignment.timeline_alignment)}`}>
                          {result.rfp_alignment.timeline_alignment}%
                        </div>
                        <div className="text-xs text-gray-600">Timeline</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className={`font-bold text-lg ${getAlignmentColor(result.rfp_alignment.technical_alignment)}`}>
                          {result.rfp_alignment.technical_alignment}%
                        </div>
                        <div className="text-xs text-gray-600">Technical</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className={`font-bold text-lg ${getAlignmentColor(result.rfp_alignment.scope_alignment)}`}>
                          {result.rfp_alignment.scope_alignment}%
                        </div>
                        <div className="text-xs text-gray-600">Scope</div>
                      </div>
                    </div>

                    {/* Mismatches */}
                    {result.rfp_alignment.mismatches && result.rfp_alignment.mismatches.length > 0 && (
                      <div className="space-y-3">
                        <h5 className="font-medium text-red-800 flex items-center gap-2">
                          <AlertTriangle className="w-4 h-4" />
                          Detected Mismatches ({result.rfp_alignment.mismatches.length})
                        </h5>
                        {result.rfp_alignment.mismatches.map((mismatch, index) => (
                          <div key={index} className={`border rounded-lg p-3 ${getSeverityColor(mismatch.severity)}`}>
                            <div className="flex items-start gap-2">
                              {getSeverityIcon(mismatch.severity)}
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium text-sm capitalize">{mismatch.type}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {mismatch.severity}
                                  </Badge>
                                </div>
                                <p className="text-sm text-gray-800 mb-2">{mismatch.message}</p>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                                  <div>
                                    <span className="font-medium">RFP Requirement:</span>
                                    <p className="text-gray-600">{mismatch.rfp_requirement}</p>
                                  </div>
                                  <div>
                                    <span className="font-medium">Proposal Value:</span>
                                    <p className="text-gray-600">{mismatch.proposal_value}</p>
                                  </div>
                                </div>
                                <div className="mt-2">
                                  <span className="font-medium text-xs">Impact:</span>
                                  <p className="text-xs text-gray-600">{mismatch.impact}</p>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

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
