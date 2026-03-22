import React, { useState } from 'react';


interface Customer {
    id: string;
    name: string;
    company: string;
    email: string;
    phone: string;
    address: string;
    requirements: string;
    fleet_requirements: string;
    status: string;
    sales_stage: string;
    created_at: string;
    updated_at: string;
}


const CustomerOnboardingDashboard: React.FC = () => {
    const [customers, setCustomers] = useState<Customer[]>([]);
    const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
    const [loading, setLoading] = useState(false);

    // Mock data for demonstration
    const mockCustomers: Customer[] = [
        {
            id: 'boggs_systems',
            name: 'Boggs Systems Corporation',
            company: 'Boggs Systems',
            email: 'contact@boggs.com',
            phone: '+1-555-ROBOTS',
            address: '123 Tech Street, Robot City, RC 12345',
            requirements: 'Cottage automation with advanced fleet management',
            fleet_requirements: '3-5 robots, mixed indoor/outdoor capabilities',
            status: 'prospect',
            sales_stage: 'initial_contact',
            created_at: '2024-01-15T00:00:00Z',
            updated_at: '2024-01-20T00:00:00Z'
        },
        {
            id: 'cottage_owner_001',
            name: 'Cottage Owner',
            company: 'Private Residence',
            email: 'owner@cottage.com',
            phone: '+1-555-COTTAGE',
            address: '456 Lakeview Drive, Cottage Town',
            requirements: 'Basic home automation with 1-2 robots',
            fleet_requirements: '1-2 robots, indoor focus',
            status: 'active',
            sales_stage: 'needs_assessment',
            created_at: '2024-02-01T00:00:00Z',
            updated_at: '2024-02-10T00:00:00Z'
        }
    ];

    React.useEffect(() => {
        setCustomers(mockCustomers);
    }, []);

    const handleAddCustomer = () => {
        const newCustomer: Customer = {
            id: `customer_${Date.now()}`,
            name: 'New Customer',
            company: 'New Company',
            email: 'new@example.com',
            phone: '+1-555-NEW',
            address: 'New Address',
            requirements: 'To be determined',
            fleet_requirements: 'To be determined',
            status: 'new',
            sales_stage: 'initial_contact',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
        
        setCustomers([...customers, newCustomer]);
    };

    const handleSelectCustomer = (customer: Customer) => {
        setSelectedCustomer(customer);
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Customer Onboarding Admin Panel</h1>
                    <p className="text-gray-600 mb-4">Manage customers, sales pipeline, and fleet deployments</p>
                </div>
                
                <div className="mb-6">
                    <button
                        onClick={handleAddCustomer}
                        className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                    >
                        Add New Customer
                    </button>
                </div>
                
                {loading ? (
                    <div className="loading-spinner">Loading customers...</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {customers.map(customer => (
                            <div key={customer.id} className="bg-white rounded-lg shadow p-6 border border-gray-200">
                                <div className="p-4">
                                    <div className="font-semibold text-lg">{customer.name}</div>
                                    <div className="text-gray-600">{customer.company}</div>
                                    <div className="text-sm text-gray-500">{customer.email}</div>
                                    <div className="text-sm text-gray-500">{customer.phone}</div>
                                    <div className="text-sm text-gray-500">{customer.address}</div>
                                    <div className="text-sm text-gray-500">{customer.requirements}</div>
                                    <div className="text-sm text-gray-500">{customer.fleet_requirements}</div>
                                </div>
                                <div className="mt-4 flex justify-between">
                                    <div>
                                        <span className="text-sm font-medium text-gray-700">Status: </span>
                                        <span className={`px-2 py-1 text-xs rounded-full ${
                                            customer.status === 'active' ? 'bg-green-100 text-green-800' :
                                            customer.status === 'prospect' ? 'bg-yellow-100 text-yellow-800' :
                                            'bg-gray-100 text-gray-800'
                                        }`}>
                                            {customer.status}
                                        </span>
                                    </div>
                                    <div className="text-right">
                                        <button
                                            onClick={() => handleSelectCustomer(customer)}
                                            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                                        >
                                            Edit
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
                
                {selectedCustomer && (
                    <div className="mt-8 p-6 bg-white rounded-lg shadow-lg border border-gray-200">
                        <h2 className="text-xl font-semibold mb-4">Customer Details</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div><strong>ID:</strong> {selectedCustomer.id}</div>
                            <div><strong>Name:</strong> {selectedCustomer.name}</div>
                            <div><strong>Company:</strong> {selectedCustomer.company}</div>
                            <div><strong>Email:</strong> {selectedCustomer.email}</div>
                            <div><strong>Phone:</strong> {selectedCustomer.phone}</div>
                            <div><strong>Address:</strong> {selectedCustomer.address}</div>
                            <div><strong>Requirements:</strong> {selectedCustomer.requirements}</div>
                            <div><strong>Fleet Needs:</strong> {selectedCustomer.fleet_requirements}</div>
                            <div><strong>Status:</strong> {selectedCustomer.status}</div>
                            <div><strong>Sales Stage:</strong> {selectedCustomer.sales_stage}</div>
                            <div><strong>Created:</strong> {new Date(selectedCustomer.created_at).toLocaleDateString()}</div>
                            <div><strong>Updated:</strong> {new Date(selectedCustomer.updated_at).toLocaleDateString()}</div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};


export default CustomerOnboardingDashboard;
