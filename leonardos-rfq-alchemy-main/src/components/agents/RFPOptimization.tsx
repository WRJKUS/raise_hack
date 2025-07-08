import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Upload, 
  FileText, 
  TrendingUp, 
  Clock, 
  DollarSign, 
  CheckCircle, 
  AlertTriangle,
  Target,
  BarChart3,
  Calendar,
  Settings
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { 
  apiClient, 
  RFPOptimizationAnalysis, 
  RFPOptimizationResponse,
  RFPActionItem 
} from '@/lib/api';

interface RFPOptimizationProps {}

export default function RFPOptimization({}: RFPOptimizationProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadedRFPId, setUploadedRFPId] = useState<string | null>(null);
  const [currentAnalysis, setCurrentAnalysis] = useState<RFPOptimizationAnalysis | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [actionItems, setActionItems] = useState<{
    immediate: RFPActionItem[];
    short_term: RFPActionItem[];
    long_term: RFPActionItem[];
  } | null>(null);
  const [activeTab, setActiveTab] = useState('upload');
  
  const { toast } = useToast();

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        toast({
          title: "Invalid file type",
          description: "Please select a PDF file",
          variant: "destructive"
        });
        return;
      }
      setSelectedFile(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const result = await apiClient.uploadRFPDocument(selectedFile);
      setUploadedRFPId(result.rfp_document_id);
      setActiveTab('analysis');
      
      toast({
        title: "RFP uploaded successfully",
        description: `${result.filename} is ready for optimization analysis`,
      });
    } catch (error) {
      console.error('Upload failed:', error);
      toast({
        title: "Upload failed",
        description: error.message || "Failed to upload RFP document",
        variant: "destructive"
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedRFPId) return;

    setIsAnalyzing(true);
    try {
      const result = await apiClient.analyzeRFPDocument(uploadedRFPId);
      setCurrentAnalysis(result.analysis);
      setCurrentSessionId(result.session_id);
      
      // Load action items
      const actionItemsResult = await apiClient.getRFPActionItems(result.session_id);
      setActionItems(actionItemsResult.action_items);
      
      setActiveTab('results');
      
      toast({
        title: "Analysis completed",
        description: `RFP optimization analysis completed with score ${result.analysis.overall_score}/${result.analysis.max_score}`,
      });
    } catch (error) {
      console.error('Analysis failed:', error);
      toast({
        title: "Analysis failed",
        description: error.message || "Failed to analyze RFP document",
        variant: "destructive"
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleActionItemToggle = async (itemId: string, completed: boolean) => {
    if (!currentSessionId) return;

    try {
      await apiClient.updateRFPActionItem(currentSessionId, itemId, completed);
      
      // Update local state
      if (actionItems) {
        const updateItems = (items: RFPActionItem[]) =>
          items.map(item => 
            item.id === itemId 
              ? { ...item, completed, completed_at: completed ? new Date().toISOString() : undefined }
              : item
          );

        setActionItems({
          immediate: updateItems(actionItems.immediate),
          short_term: updateItems(actionItems.short_term),
          long_term: updateItems(actionItems.long_term)
        });
      }

      toast({
        title: completed ? "Action item completed" : "Action item reopened",
        description: "Action item status updated successfully",
      });
    } catch (error) {
      console.error('Failed to update action item:', error);
      toast({
        title: "Update failed",
        description: "Failed to update action item status",
        variant: "destructive"
      });
    }
  };

  const getDimensionIcon = (dimension: string) => {
    switch (dimension) {
      case 'timeline': return <Clock className="w-4 h-4" />;
      case 'requirements': return <FileText className="w-4 h-4" />;
      case 'cost': return <DollarSign className="w-4 h-4" />;
      case 'tco': return <TrendingUp className="w-4 h-4" />;
      default: return <Target className="w-4 h-4" />;
    }
  };

  const getDimensionColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const renderDimensionCard = (title: string, analysis: any, icon: React.ReactNode) => (
    <Card className="bg-white shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          {icon}
          {title}
          <Badge variant="outline" className={getDimensionColor(analysis.score)}>
            {analysis.score}/10
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-medium text-sm text-gray-700 mb-2">Key Findings</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {analysis.findings.slice(0, 2).map((finding: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-500 mt-1">•</span>
                {finding}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4 className="font-medium text-sm text-gray-700 mb-2">Recommendations</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {analysis.recommendations.slice(0, 2).map((rec: string, index: number) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-green-500 mt-1">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );

  const renderActionItems = (items: RFPActionItem[], title: string, icon: React.ReactNode) => (
    <Card className="bg-white shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {icon}
          {title}
          <Badge variant="outline">{items.length}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="flex items-start gap-3 p-3 border rounded-lg">
              <Checkbox
                checked={item.completed}
                onCheckedChange={(checked) => handleActionItemToggle(item.id, checked as boolean)}
                className="mt-1"
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  {getDimensionIcon(item.dimension)}
                  <h4 className={`font-medium text-sm ${item.completed ? 'line-through text-gray-500' : ''}`}>
                    {item.title}
                  </h4>
                </div>
                <p className={`text-sm ${item.completed ? 'line-through text-gray-400' : 'text-gray-600'}`}>
                  {item.description}
                </p>
                {item.completed && item.completed_at && (
                  <p className="text-xs text-green-600 mt-1">
                    Completed: {new Date(item.completed_at).toLocaleDateString()}
                  </p>
                )}
              </div>
            </div>
          ))}
          {items.length === 0 && (
            <p className="text-gray-500 text-center py-4">No action items in this category</p>
          )}
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            RFP Optimization AI Agent
          </CardTitle>
          <CardDescription>
            Upload RFP documents and get actionable optimization recommendations across four critical dimensions
          </CardDescription>
        </CardHeader>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="upload">Upload RFP</TabsTrigger>
          <TabsTrigger value="analysis" disabled={!uploadedRFPId}>Analysis</TabsTrigger>
          <TabsTrigger value="results" disabled={!currentAnalysis}>Results</TabsTrigger>
          <TabsTrigger value="actions" disabled={!actionItems}>Action Items</TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-4">
          <Card className="bg-white shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Upload RFP Document
              </CardTitle>
              <CardDescription>
                Select a PDF RFP document to analyze for optimization opportunities
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileSelect}
                  className="hidden"
                  id="rfp-upload"
                />
                <label htmlFor="rfp-upload" className="cursor-pointer">
                  <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-gray-700 mb-2">
                    {selectedFile ? selectedFile.name : 'Select RFP Document'}
                  </p>
                  <p className="text-sm text-gray-500">
                    PDF files only, up to 10MB
                  </p>
                </label>
              </div>
              
              {selectedFile && (
                <div className="flex justify-center">
                  <Button 
                    onClick={handleUpload} 
                    disabled={isUploading}
                    className="w-full max-w-md"
                  >
                    {isUploading ? 'Uploading...' : 'Upload RFP Document'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-4">
          <Card className="bg-white shadow-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Start RFP Optimization Analysis
              </CardTitle>
              <CardDescription>
                Analyze your RFP across four critical dimensions for optimization recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center space-y-4">
                <p className="text-gray-600">
                  Ready to analyze your RFP document for optimization opportunities
                </p>
                <Button 
                  onClick={handleAnalyze} 
                  disabled={isAnalyzing}
                  size="lg"
                  className="w-full max-w-md"
                >
                  {isAnalyzing ? 'Analyzing...' : 'Start RFP Optimization Analysis'}
                </Button>
                {isAnalyzing && (
                  <div className="space-y-2">
                    <Progress value={33} className="w-full max-w-md mx-auto" />
                    <p className="text-sm text-gray-500">Analyzing RFP dimensions...</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-6">
          {currentAnalysis && (
            <>
              {/* Executive Summary */}
              <Card className="bg-white shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Executive Summary
                    <Badge variant="outline" className="ml-auto">
                      {currentAnalysis.overall_score}/{currentAnalysis.max_score}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 mb-4">{currentAnalysis.executive_summary}</p>
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm text-gray-700">Priority Actions:</h4>
                    <ul className="space-y-1">
                      {currentAnalysis.priority_actions.map((action, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                          <span className="text-red-500 font-bold mt-1">{index + 1}.</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>

              {/* Four Dimensions Analysis */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {renderDimensionCard(
                  "Timeline Feasibility",
                  currentAnalysis.timeline_feasibility,
                  <Clock className="w-5 h-5" />
                )}
                {renderDimensionCard(
                  "Requirements Clarity",
                  currentAnalysis.requirements_clarity,
                  <FileText className="w-5 h-5" />
                )}
                {renderDimensionCard(
                  "Cost Structure & Flexibility",
                  currentAnalysis.cost_flexibility,
                  <DollarSign className="w-5 h-5" />
                )}
                {renderDimensionCard(
                  "Total Cost of Ownership",
                  currentAnalysis.tco_analysis,
                  <TrendingUp className="w-5 h-5" />
                )}
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="actions" className="space-y-6">
          {actionItems && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {renderActionItems(actionItems.immediate, "Immediate (0-1 week)", <AlertTriangle className="w-5 h-5 text-red-500" />)}
              {renderActionItems(actionItems.short_term, "Short-term (1-4 weeks)", <Calendar className="w-5 h-5 text-yellow-500" />)}
              {renderActionItems(actionItems.long_term, "Long-term (1-3 months)", <Target className="w-5 h-5 text-green-500" />)}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
