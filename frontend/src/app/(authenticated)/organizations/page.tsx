"use client"

import { useState } from "react"
import { 
  Plus, 
  Search, 
  Building2, 
  Users, 
  Settings, 
  MoreHorizontal,
  Edit,
  Trash2,
  UserPlus,
  Eye,
  MapPin,
  Mail,
  Phone,
  Globe,
  DollarSign,
  TrendingUp
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"

// Mock data for organizations
const organizations = [
  {
    id: "1",
    name: "TechCorp Solutions",
    type: "Client",
    industry: "Technology",
    location: "San Francisco, CA",
    employees: 2500,
    activeRfps: 8,
    totalValue: 1250000,
    status: "active",
    contactEmail: "procurement@techcorp.com",
    contactPhone: "+1 (555) 123-4567",
    website: "www.techcorp.com",
    logo: "/api/placeholder/40/40"
  },
  {
    id: "2", 
    name: "Global Manufacturing Inc",
    type: "Client",
    industry: "Manufacturing",
    location: "Detroit, MI",
    employees: 15000,
    activeRfps: 12,
    totalValue: 3200000,
    status: "active",
    contactEmail: "rfp@globalmanuf.com",
    contactPhone: "+1 (555) 987-6543",
    website: "www.globalmanuf.com",
    logo: "/api/placeholder/40/40"
  },
  {
    id: "3",
    name: "Healthcare Systems Alliance", 
    type: "Client",
    industry: "Healthcare",
    location: "Boston, MA",
    employees: 8500,
    activeRfps: 5,
    totalValue: 850000,
    status: "active",
    contactEmail: "procurement@hsa.org",
    contactPhone: "+1 (555) 456-7890", 
    website: "www.hsa.org",
    logo: "/api/placeholder/40/40"
  },
  {
    id: "4",
    name: "Strategic Consulting Group",
    type: "Partner",
    industry: "Consulting", 
    location: "New York, NY",
    employees: 450,
    activeRfps: 3,
    totalValue: 180000,
    status: "active",
    contactEmail: "partnerships@scg.com",
    contactPhone: "+1 (555) 321-0987",
    website: "www.scg.com", 
    logo: "/api/placeholder/40/40"
  }
]

export default function OrganizationsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedType, setSelectedType] = useState("all")

  const filteredOrganizations = organizations.filter(org => {
    const matchesSearch = org.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         org.industry.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         org.location.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = selectedType === "all" || org.type.toLowerCase() === selectedType
    return matchesSearch && matchesType
  })

  const getStatusBadge = (status: string) => {
    const variants = {
      active: { color: "bg-green-100 text-green-800", text: "Active" },
      inactive: { color: "bg-gray-100 text-gray-800", text: "Inactive" },
      pending: { color: "bg-yellow-100 text-yellow-800", text: "Pending" }
    }
    
    const config = variants[status as keyof typeof variants] || variants.active
    return <Badge className={config.color}>{config.text}</Badge>
  }

  const getTypeBadge = (type: string) => {
    const variants = {
      client: { color: "bg-blue-100 text-blue-800", text: "Client" },
      partner: { color: "bg-purple-100 text-purple-800", text: "Partner" },
      vendor: { color: "bg-orange-100 text-orange-800", text: "Vendor" }
    }
    
    const config = variants[type.toLowerCase() as keyof typeof variants] || variants.client
    return <Badge className={config.color}>{config.text}</Badge>
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Organizations
          </h1>
          <p className="text-muted-foreground text-lg">
            Manage client relationships and business partnerships
          </p>
        </div>
        <Button 
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Organization
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Organizations</CardTitle>
            <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
              <Building2 className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{organizations.length}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              {organizations.filter(o => o.status === 'active').length} active partnerships
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Active RFPs</CardTitle>
            <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg">
              <Users className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">
              {organizations.reduce((sum, org) => sum + org.activeRfps, 0)}
            </div>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              Across all organizations
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Total Value</CardTitle>
            <div className="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg">
              <DollarSign className="h-4 w-4 text-purple-600 dark:text-purple-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
              ${(organizations.reduce((sum, org) => sum + org.totalValue, 0) / 1000000).toFixed(1)}M
            </div>
            <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
              Total pipeline value
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700 dark:text-orange-300">Avg Deal Size</CardTitle>
            <div className="p-2 bg-orange-100 dark:bg-orange-800 rounded-lg">
              <TrendingUp className="h-4 w-4 text-orange-600 dark:text-orange-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">
              ${((organizations.reduce((sum, org) => sum + org.totalValue, 0) / organizations.reduce((sum, org) => sum + org.activeRfps, 0)) / 1000).toFixed(0)}K
            </div>
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              Per RFP opportunity
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search organizations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Settings className="mr-2 h-4 w-4" />
              Type: {selectedType === 'all' ? 'All' : selectedType}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setSelectedType("all")}>
              All Types
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedType("client")}>
              Clients
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedType("partner")}>
              Partners
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedType("vendor")}>
              Vendors
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Organizations Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredOrganizations.map((org) => (
          <Card key={org.id} className="border-0 shadow-lg hover:shadow-xl transition-all duration-200 group">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={org.logo} alt={org.name} />
                    <AvatarFallback className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold">
                      {org.name.substring(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-lg">{org.name}</CardTitle>
                    <div className="flex items-center space-x-2 mt-1">
                      {getTypeBadge(org.type)}
                      {getStatusBadge(org.status)}
                    </div>
                  </div>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem>
                      <Eye className="mr-2 h-4 w-4" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit Organization
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <UserPlus className="mr-2 h-4 w-4" />
                      Add Contact
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center text-sm text-muted-foreground">
                  <Building2 className="w-4 h-4 mr-2" />
                  {org.industry}
                </div>
                <div className="flex items-center text-sm text-muted-foreground">
                  <MapPin className="w-4 h-4 mr-2" />
                  {org.location}
                </div>
                <div className="flex items-center text-sm text-muted-foreground">
                  <Users className="w-4 h-4 mr-2" />
                  {org.employees.toLocaleString()} employees
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm border-t pt-4">
                <div>
                  <div className="text-muted-foreground">Active RFPs</div>
                  <div className="font-semibold text-lg">{org.activeRfps}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Pipeline Value</div>
                  <div className="font-semibold text-lg">${(org.totalValue / 1000).toFixed(0)}K</div>
                </div>
              </div>

              <div className="flex space-x-2">
                <Button size="sm" className="flex-1">
                  <Eye className="mr-2 h-3 w-3" />
                  View
                </Button>
                <Button size="sm" variant="outline" className="flex-1">
                  <Mail className="mr-2 h-3 w-3" />
                  Contact
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}