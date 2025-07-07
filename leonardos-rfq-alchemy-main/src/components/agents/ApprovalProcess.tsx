
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { CheckCircle, UserPlus, Mail, Clock, ArrowRight, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const ApprovalProcess = () => {
  const [workflows, setWorkflows] = useState([
    {
      id: 1,
      name: 'Standard RFP Approval',
      approvers: [
        { id: 1, name: 'Sarah Johnson', email: 'sarah.j@company.com', role: 'CTO', required: true, order: 1 },
        { id: 2, name: 'Mike Chen', email: 'mike.c@company.com', role: 'CFO', required: true, order: 2 },
        { id: 3, name: 'Lisa Park', email: 'lisa.p@company.com', role: 'Legal Counsel', required: false, order: 3 }
      ],
      averageTime: '3.2 days',
      isActive: true
    },
    {
      id: 2,
      name: 'High-Value RFQ Process',
      approvers: [
        { id: 4, name: 'John Smith', email: 'john.s@company.com', role: 'VP Engineering', required: true, order: 1 },
        { id: 5, name: 'Sarah Johnson', email: 'sarah.j@company.com', role: 'CTO', required: true, order: 2 },
        { id: 6, name: 'Mike Chen', email: 'mike.c@company.com', role: 'CFO', required: true, order: 3 },
        { id: 7, name: 'David Kim', email: 'david.k@company.com', role: 'CEO', required: true, order: 4 }
      ],
      averageTime: '5.8 days',
      isActive: true
    }
  ]);

  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [newApprover, setNewApprover] = useState({
    name: '',
    email: '',
    role: '',
    required: true
  });
  const [isAddingApprover, setIsAddingApprover] = useState(false);
  const { toast } = useToast();

  const createNewWorkflow = () => {
    const newWorkflow = {
      id: Date.now(),
      name: 'New Approval Workflow',
      approvers: [],
      averageTime: 'Not calculated',
      isActive: false
    };
    setWorkflows(prev => [...prev, newWorkflow]);
    setSelectedWorkflow(newWorkflow);
    toast({
      title: "New workflow created",
      description: "You can now configure approvers and settings",
    });
  };

  const addApprover = () => {
    if (!newApprover.name || !newApprover.email || !selectedWorkflow) return;

    const approver = {
      id: Date.now(),
      ...newApprover,
      order: selectedWorkflow.approvers.length + 1
    };

    const updatedWorkflows = workflows.map(w => 
      w.id === selectedWorkflow.id 
        ? { ...w, approvers: [...w.approvers, approver] }
        : w
    );

    setWorkflows(updatedWorkflows);
    setSelectedWorkflow(prev => ({ ...prev, approvers: [...prev.approvers, approver] }));
    setNewApprover({ name: '', email: '', role: '', required: true });
    setIsAddingApprover(false);

    toast({
      title: "Approver added",
      description: `${approver.name} has been added to the workflow`,
    });
  };

  const removeApprover = (approverId) => {
    const updatedWorkflows = workflows.map(w => 
      w.id === selectedWorkflow.id 
        ? { ...w, approvers: w.approvers.filter(a => a.id !== approverId) }
        : w
    );

    setWorkflows(updatedWorkflows);
    setSelectedWorkflow(prev => ({ 
      ...prev, 
      approvers: prev.approvers.filter(a => a.id !== approverId) 
    }));

    toast({
      title: "Approver removed",
      description: "The approver has been removed from the workflow",
    });
  };

  const toggleWorkflowActive = (workflowId) => {
    const updatedWorkflows = workflows.map(w => 
      w.id === workflowId ? { ...w, isActive: !w.isActive } : w
    );
    setWorkflows(updatedWorkflows);
    
    if (selectedWorkflow && selectedWorkflow.id === workflowId) {
      setSelectedWorkflow(prev => ({ ...prev, isActive: !prev.isActive }));
    }
  };

  const reorderApprovers = (approvers) => {
    return approvers
      .sort((a, b) => a.order - b.order)
      .map((approver, index) => ({ ...approver, order: index + 1 }));
  };

  return (
    <div className="space-y-6">
      <Card className="bg-white shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5" />
            Agent 3: Approval Process Setup
          </CardTitle>
          <CardDescription>
            Configure approval workflows with roles, sequences, and timing requirements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Button onClick={createNewWorkflow} className="bg-blue-600 hover:bg-blue-700">
              <UserPlus className="w-4 h-4 mr-2" />
              Create New Workflow
            </Button>
            <p className="text-sm text-gray-600">
              {workflows.length} workflow(s) configured • {workflows.filter(w => w.isActive).length} active
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Workflow List */}
        <Card className="bg-white shadow-sm">
          <CardHeader>
            <CardTitle>Approval Workflows</CardTitle>
            <CardDescription>Manage and configure your approval processes</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {workflows.map((workflow) => (
              <div
                key={workflow.id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                  selectedWorkflow?.id === workflow.id 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedWorkflow(workflow)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-gray-900">{workflow.name}</h4>
                  <div className="flex items-center gap-2">
                    <Badge variant={workflow.isActive ? 'default' : 'secondary'}>
                      {workflow.isActive ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>{workflow.approvers.length} approver(s)</span>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span>{workflow.averageTime}</span>
                  </div>
                </div>
                
                {/* Approver Chain Preview */}
                <div className="mt-3 flex items-center gap-2 overflow-x-auto">
                  {reorderApprovers(workflow.approvers).slice(0, 3).map((approver, index) => (
                    <div key={approver.id} className="flex items-center gap-1 flex-shrink-0">
                      <div className="w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center text-xs font-medium">
                        {approver.name.charAt(0)}
                      </div>
                      {index < workflow.approvers.length - 1 && index < 2 && (
                        <ArrowRight className="w-3 h-3 text-gray-400" />
                      )}
                    </div>
                  ))}
                  {workflow.approvers.length > 3 && (
                    <span className="text-xs text-gray-500">+{workflow.approvers.length - 3} more</span>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Workflow Configuration */}
        {selectedWorkflow && (
          <Card className="bg-white shadow-sm">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{selectedWorkflow.name}</CardTitle>
                  <CardDescription>Configure approvers and sequence</CardDescription>
                </div>
                <Button
                  variant={selectedWorkflow.isActive ? 'destructive' : 'default'}
                  size="sm"
                  onClick={() => toggleWorkflowActive(selectedWorkflow.id)}
                >
                  {selectedWorkflow.isActive ? 'Deactivate' : 'Activate'}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Workflow Settings */}
              <div className="space-y-4">
                <div>
                  <Label htmlFor="workflow-name">Workflow Name</Label>
                  <Input
                    id="workflow-name"
                    value={selectedWorkflow.name}
                    onChange={(e) => {
                      const updatedWorkflows = workflows.map(w => 
                        w.id === selectedWorkflow.id ? { ...w, name: e.target.value } : w
                      );
                      setWorkflows(updatedWorkflows);
                      setSelectedWorkflow(prev => ({ ...prev, name: e.target.value }));
                    }}
                  />
                </div>
              </div>

              {/* Approvers List */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Approvers ({selectedWorkflow.approvers.length})</h4>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setIsAddingApprover(true)}
                  >
                    <UserPlus className="w-4 h-4 mr-2" />
                    Add Approver
                  </Button>
                </div>

                {reorderApprovers(selectedWorkflow.approvers).map((approver, index) => (
                  <div key={approver.id} className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center font-medium text-blue-800">
                      {index + 1}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="font-medium text-gray-900">{approver.name}</p>
                        <Badge variant={approver.required ? 'default' : 'secondary'} className="text-xs">
                          {approver.required ? 'Required' : 'Optional'}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{approver.role}</p>
                      <div className="flex items-center gap-1 text-xs text-gray-500">
                        <Mail className="w-3 h-3" />
                        <span>{approver.email}</span>
                      </div>
                    </div>

                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeApprover(approver.id)}
                      className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                ))}

                {selectedWorkflow.approvers.length === 0 && (
                  <div className="text-center py-8 text-gray-500">
                    <UserPlus className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p>No approvers configured</p>
                    <p className="text-sm">Add approvers to set up the workflow sequence</p>
                  </div>
                )}
              </div>

              {/* Add Approver Form */}
              {isAddingApprover && (
                <Card className="border-2 border-dashed border-blue-300 bg-blue-50">
                  <CardContent className="pt-6 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="approver-name">Name</Label>
                        <Input
                          id="approver-name"
                          value={newApprover.name}
                          onChange={(e) => setNewApprover(prev => ({ ...prev, name: e.target.value }))}
                          placeholder="Enter full name"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="approver-email">Email</Label>
                        <Input
                          id="approver-email"
                          type="email"
                          value={newApprover.email}
                          onChange={(e) => setNewApprover(prev => ({ ...prev, email: e.target.value }))}
                          placeholder="email@company.com"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="approver-role">Role</Label>
                        <Select
                          value={newApprover.role}
                          onValueChange={(value) => setNewApprover(prev => ({ ...prev, role: value }))}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select role" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="CEO">CEO</SelectItem>
                            <SelectItem value="CTO">CTO</SelectItem>
                            <SelectItem value="CFO">CFO</SelectItem>
                            <SelectItem value="VP Engineering">VP Engineering</SelectItem>
                            <SelectItem value="Legal Counsel">Legal Counsel</SelectItem>
                            <SelectItem value="Procurement Manager">Procurement Manager</SelectItem>
                            <SelectItem value="Department Head">Department Head</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      
                      <div className="flex items-center space-x-2 pt-6">
                        <Checkbox
                          id="required-approver"
                          checked={newApprover.required}
                          onCheckedChange={(checked) => setNewApprover(prev => ({ ...prev, required: checked }))}
                        />
                        <Label htmlFor="required-approver" className="text-sm">Required approver</Label>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 pt-2">
                      <Button onClick={addApprover} size="sm">
                        Add Approver
                      </Button>
                      <Button
                        onClick={() => {
                          setIsAddingApprover(false);
                          setNewApprover({ name: '', email: '', role: '', required: true });
                        }}
                        variant="outline"
                        size="sm"
                      >
                        Cancel
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ApprovalProcess;
