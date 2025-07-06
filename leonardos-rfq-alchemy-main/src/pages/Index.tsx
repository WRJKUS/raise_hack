
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { BarChart3, FileText, MessageSquare, CheckCircle, Calculator, TrendingUp, Clock, Users } from 'lucide-react';
import ComparativeAnalysis from '@/components/agents/ComparativeAnalysis';
import ChatAssistant from '@/components/agents/ChatAssistant';
import ApprovalProcess from '@/components/agents/ApprovalProcess';
import QuoteManagement from '@/components/agents/QuoteManagement';

const Index = () => {
  const [activeTab, setActiveTab] = useState('overview');

  const overviewStats = [
    { title: 'Active RFPs', value: '12', icon: FileText, trend: '+2 this week' },
    { title: 'Pending Approvals', value: '5', icon: Clock, trend: '3 urgent' },
    { title: 'RFQs Sent', value: '28', icon: Calculator, trend: '+8 this month' },
    { title: 'Active Vendors', value: '47', icon: Users, trend: '12 new contacts' }
  ];

  const recentActivity = [
    { action: 'New proposal analyzed', vendor: 'TechCorp Solutions', time: '2 hours ago', status: 'completed' },
    { action: 'RFQ sent to vendor', vendor: 'Digital Dynamics', time: '4 hours ago', status: 'pending' },
    { action: 'Approval workflow completed', vendor: 'InnovateTech', time: '1 day ago', status: 'completed' },
    { action: 'Quote comparison updated', vendor: 'Multiple vendors', time: '2 days ago', status: 'completed' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">AI Leonardo's RFP/RFQ Management Platform</h1>
          <p className="text-gray-600 mt-1">Streamline your proposal analysis and quote management workflow</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5 bg-white border border-gray-200 p-1 rounded-lg">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Analysis Agent
            </TabsTrigger>
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat Assistant
            </TabsTrigger>
            <TabsTrigger value="approval" className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Approval Setup
            </TabsTrigger>
            <TabsTrigger value="quotes" className="flex items-center gap-2">
              <Calculator className="w-4 h-4" />
              Quote Manager
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {overviewStats.map((stat, index) => (
                <Card key={index} className="bg-white shadow-sm hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                        <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                        <p className="text-sm text-green-600 mt-1">{stat.trend}</p>
                      </div>
                      <div className="p-3 bg-blue-50 rounded-full">
                        <stat.icon className="w-6 h-6 text-blue-600" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card className="bg-white shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    Recent Activity
                  </CardTitle>
                  <CardDescription>Latest updates from your RFP/RFQ workflow</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {recentActivity.map((activity, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{activity.action}</p>
                        <p className="text-sm text-gray-600">{activity.vendor}</p>
                        <p className="text-xs text-gray-500">{activity.time}</p>
                      </div>
                      <Badge variant={activity.status === 'completed' ? 'default' : 'secondary'}>
                        {activity.status}
                      </Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card className="bg-white shadow-sm">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Workflow Progress
                  </CardTitle>
                  <CardDescription>Current status of your RFP/RFQ pipeline</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Proposal Analysis</span>
                      <span className="text-sm text-gray-600">8/12 completed</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: '67%' }}></div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Approval Workflows</span>
                      <span className="text-sm text-gray-600">3/5 approved</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{ width: '60%' }}></div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">Quote Requests</span>
                      <span className="text-sm text-gray-600">21/28 responses</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="analysis">
            <ComparativeAnalysis />
          </TabsContent>

          <TabsContent value="chat">
            <ChatAssistant />
          </TabsContent>

          <TabsContent value="approval">
            <ApprovalProcess />
          </TabsContent>

          <TabsContent value="quotes">
            <QuoteManagement />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Index;
