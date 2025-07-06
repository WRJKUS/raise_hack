
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Calculator, Mail, Send, TrendingUp, Award, Clock, DollarSign, Star } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const QuoteManagement = () => {
  const [selectedVendors, setSelectedVendors] = useState([]);
  const [rfqMessage, setRfqMessage] = useState(
    "Dear Vendor,\n\nWe are requesting a quote for the project outlined in the attached RFP. Please provide your detailed pricing and timeline.\n\nBest regards,\nProcurement Team"
  );
  const [sentRfqs, setSentRfqs] = useState([
    {
      id: 1,
      vendor: 'TechCorp Solutions',
      email: 'john.doe@techcorp.com',
      sentDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
      status: 'responded',
      quote: {
        amount: 125000,
        timeline: '8 weeks',
        score: 92
      }
    },
    {
      id: 2,
      vendor: 'Digital Dynamics',
      email: 'sarah.wilson@digitaldynamics.com',
      sentDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
      status: 'responded',
      quote: {
        amount: 148000,
        timeline: '12 weeks',
        score: 78
      }
    },
    {
      id: 3,
      vendor: 'CloudTech Partners',
      email: 'mike.johnson@cloudtech.com',
      sentDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      status: 'pending',
      quote: null
    }
  ]);

  const [quoteComparison, setQuoteComparison] = useState([
    {
      vendor: 'TechCorp Solutions',
      quote: 125000,
      timeline: '8 weeks',
      efficiencyScore: 92,
      valueRating: 'A+',
      strengths: ['Best value', 'Fastest delivery', 'Proven expertise'],
      concerns: ['Tight timeline risk']
    },
    {
      vendor: 'Digital Dynamics',
      quote: 148000,
      timeline: '12 weeks',
      efficiencyScore: 78,
      valueRating: 'B+',
      strengths: ['Comprehensive solution', 'Local support', 'Good track record'],
      concerns: ['Higher cost', 'Longer timeline']
    }
  ]);

  const availableVendors = [
    { id: 1, name: 'TechCorp Solutions', email: 'john.doe@techcorp.com', contacted: true },
    { id: 2, name: 'Digital Dynamics', email: 'sarah.wilson@digitaldynamics.com', contacted: true },
    { id: 3, name: 'CloudTech Partners', email: 'mike.johnson@cloudtech.com', contacted: true },
    { id: 4, name: 'Innovation Labs', email: 'contact@innovationlabs.com', contacted: false },
    { id: 5, name: 'NextGen Systems', email: 'sales@nextgensys.com', contacted: false },
    { id: 6, name: 'Quantum Solutions', email: 'info@quantumsol.com', contacted: false }
  ];

  const { toast } = useToast();

  const toggleVendorSelection = (vendorId) => {
    setSelectedVendors(prev => 
      prev.includes(vendorId) 
        ? prev.filter(id => id !== vendorId)
        : [...prev, vendorId]
    );
  };

  const sendRfqs = () => {
    if (selectedVendors.length === 0) {
      toast({
        title: "No vendors selected",
        description: "Please select at least one vendor to send RFQ requests",
        variant: "destructive"
      });
      return;
    }

    const selectedVendorData = availableVendors.filter(v => selectedVendors.includes(v.id));
    
    const newRfqs = selectedVendorData.map(vendor => ({
      id: Date.now() + vendor.id,
      vendor: vendor.name,
      email: vendor.email,
      sentDate: new Date(),
      status: 'pending',
      quote: null
    }));

    setSentRfqs(prev => [...prev, ...newRfqs]);
    setSelectedVendors([]);

    toast({
      title: "RFQ requests sent",
      description: `Sent to ${selectedVendorData.length} vendor(s): ${selectedVendorData.map(v => v.name).join(', ')}`,
    });
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'responded':
        return <Badge variant="default" className="bg-green-600">Responded</Badge>;
      case 'pending':
        return <Badge variant="secondary">Pending</Badge>;
      case 'overdue':
        return <Badge variant="destructive">Overdue</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getValueRatingColor = (rating) => {
    switch (rating) {
      case 'A+':
      case 'A':
        return 'text-green-600 bg-green-100';
      case 'B+':
      case 'B':
        return 'text-yellow-600 bg-yellow-100';
      case 'C':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const calculateSavings = (quotes) => {
    if (quotes.length < 2) return 0;
    const amounts = quotes.map(q => q.quote);
    const max = Math.max(...amounts);
    const min = Math.min(...amounts);
    return max - min;
  };

  return (
    <div className="space-y-6">
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="w-5 h-5" />
            Agent 4: Quote Management & Comparison
          </CardTitle>
          <CardDescription>
            Send RFQ requests to vendors and compare received quotes with efficiency analysis
          </CardDescription>
        </CardHeader>
      </Card>

      {/* RFQ Request Section */}
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Send className="w-5 h-5" />
            Send RFQ Requests
          </CardTitle>
          <CardDescription>Select vendors and send quote requests</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Vendor Selection */}
          <div>
            <h4 className="font-medium mb-4">Available Vendors ({availableVendors.length})</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {availableVendors.map((vendor) => (
                <div
                  key={vendor.id}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedVendors.includes(vendor.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => toggleVendorSelection(vendor.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h5 className="font-medium text-gray-900">{vendor.name}</h5>
                    {vendor.contacted && (
                      <Badge variant="outline" className="text-xs">Previously contacted</Badge>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Mail className="w-3 h-3" />
                    <span>{vendor.email}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* RFQ Message */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              RFQ Message Template
            </label>
            <Textarea
              value={rfqMessage}
              onChange={(e) => setRfqMessage(e.target.value)}
              className="h-32"
              placeholder="Enter your RFQ message..."
            />
          </div>

          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {selectedVendors.length} vendor(s) selected
            </p>
            <Button
              onClick={sendRfqs}
              disabled={selectedVendors.length === 0}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Send className="w-4 h-4 mr-2" />
              Send RFQ Requests
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Sent RFQs Tracking */}
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            RFQ Tracking ({sentRfqs.length})
          </CardTitle>
          <CardDescription>Monitor sent requests and response status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sentRfqs.map((rfq) => (
              <div key={rfq.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h5 className="font-medium text-gray-900">{rfq.vendor}</h5>
                    {getStatusBadge(rfq.status)}
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Mail className="w-3 h-3" />
                      <span>{rfq.email}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      <span>Sent {rfq.sentDate.toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>
                
                {rfq.quote && (
                  <div className="text-right">
                    <p className="font-bold text-lg text-green-600">
                      {formatCurrency(rfq.quote.amount)}
                    </p>
                    <p className="text-sm text-gray-600">{rfq.quote.timeline}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <Star className="w-3 h-3 text-yellow-500" />
                      <span className="text-sm font-medium">{rfq.quote.score}/100</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quote Comparison */}
      {quoteComparison.length > 0 && (
        <Card className="bg-white shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Quote Comparison & Analysis
            </CardTitle>
            <CardDescription>
              Efficiency scoring and value analysis of received quotes
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg">
              <div className="text-center">
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(Math.min(...quoteComparison.map(q => q.quote)))}
                </p>
                <p className="text-sm text-gray-600">Lowest Quote</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(calculateSavings(quoteComparison))}
                </p>
                <p className="text-sm text-gray-600">Potential Savings</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-600">
                  {Math.min(...quoteComparison.map(q => parseInt(q.timeline)))} weeks
                </p>
                <p className="text-sm text-gray-600">Fastest Timeline</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-orange-600">
                  {Math.max(...quoteComparison.map(q => q.efficiencyScore))}%
                </p>
                <p className="text-sm text-gray-600">Top Efficiency Score</p>
              </div>
            </div>

            {/* Detailed Comparison */}
            <div className="space-y-4">
              {quoteComparison
                .sort((a, b) => b.efficiencyScore - a.efficiencyScore)
                .map((quote, index) => (
                <Card key={quote.vendor} className={`border-2 ${index === 0 ? 'border-green-200 bg-green-50' : 'border-gray-200'}`}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <h4 className="text-xl font-bold text-gray-900">{quote.vendor}</h4>
                        {index === 0 && (
                          <Badge className="bg-green-600">
                            <Award className="w-3 h-3 mr-1" />
                            Best Value
                          </Badge>
                        )}
                      </div>
                      <div className={`px-3 py-1 rounded-full font-bold text-lg ${getValueRatingColor(quote.valueRating)}`}>
                        {quote.valueRating}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                      <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                        <DollarSign className="w-6 h-6 text-green-600 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-gray-900">{formatCurrency(quote.quote)}</p>
                        <p className="text-sm text-gray-600">Quote Amount</p>
                      </div>
                      
                      <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                        <Clock className="w-6 h-6 text-blue-600 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-gray-900">{quote.timeline}</p>
                        <p className="text-sm text-gray-600">Timeline</p>
                      </div>
                      
                      <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                        <TrendingUp className="w-6 h-6 text-purple-600 mx-auto mb-2" />
                        <p className="text-2xl font-bold text-gray-900">{quote.efficiencyScore}%</p>
                        <p className="text-sm text-gray-600">Efficiency Score</p>
                        <Progress value={quote.efficiencyScore} className="mt-2" />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h5 className="font-medium text-green-800 mb-3 flex items-center gap-2">
                          <Star className="w-4 h-4" />
                          Key Strengths
                        </h5>
                        <ul className="space-y-2">
                          {quote.strengths.map((strength, idx) => (
                            <li key={idx} className="flex items-start gap-2">
                              <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                              <span className="text-sm text-gray-700">{strength}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h5 className="font-medium text-red-800 mb-3 flex items-center gap-2">
                          <Star className="w-4 h-4" />
                          Considerations
                        </h5>
                        <ul className="space-y-2">
                          {quote.concerns.map((concern, idx) => (
                            <li key={idx} className="flex items-start gap-2">
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
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default QuoteManagement;
