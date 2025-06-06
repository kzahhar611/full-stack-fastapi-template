"use client"

import { useState } from "react"
import { 
  Plus, 
  Search, 
  FileText, 
  Settings, 
  MoreHorizontal,
  Edit,
  Copy,
  Trash2,
  Download,
  Eye,
  Star,
  Clock,
  Building2
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"

// Mock data for templates
const templates = [
  {
    id: "1",
    name: "IT Infrastructure RFP",
    description: "Comprehensive template for IT infrastructure procurement including servers, networking, and cloud services",
    category: "Technology",
    industry: "General",
    lastModified: "2 days ago",
    usageCount: 45,
    rating: 4.8,
    status: "published",
    author: "Sarah Johnson",
    fields: 28
  },
  {
    id: "2",
    name: "Software Development Services",
    description: "Template for custom software development projects including web applications, mobile apps, and enterprise solutions",
    category: "Technology",
    industry: "Software",
    lastModified: "1 week ago",
    usageCount: 67,
    rating: 4.9,
    status: "published",
    author: "Michael Chen",
    fields: 35
  },
  {
    id: "3",
    name: "Marketing Campaign RFP",
    description: "Comprehensive template for marketing campaign proposals including digital marketing, branding, and advertising services",
    category: "Marketing",
    industry: "General",
    lastModified: "3 days ago",
    usageCount: 23,
    rating: 4.6,
    status: "published",
    author: "Emily Rodriguez",
    fields: 22
  },
  {
    id: "4",
    name: "Healthcare Equipment Procurement",
    description: "Specialized template for medical equipment procurement with compliance requirements and safety standards",
    category: "Healthcare",
    industry: "Healthcare",
    lastModified: "5 days ago",
    usageCount: 18,
    rating: 4.7,
    status: "published",
    author: "David Kim",
    fields: 31
  },
  {
    id: "5",
    name: "Financial Services Consulting",
    description: "Template for financial consulting services including risk assessment, compliance, and strategic planning",
    category: "Consulting",
    industry: "Finance",
    lastModified: "1 day ago",
    usageCount: 12,
    rating: 4.5,
    status: "draft",
    author: "Lisa Thompson",
    fields: 26
  },
  {
    id: "6",
    name: "Construction & Engineering",
    description: "Template for construction and engineering projects with safety requirements and project timeline specifications",
    category: "Construction",
    industry: "Construction",
    lastModified: "1 week ago",
    usageCount: 34,
    rating: 4.8,
    status: "published",
    author: "John Davis",
    fields: 42
  }
]

const categories = [
  { label: "All Categories", value: "all" },
  { label: "Technology", value: "technology" },
  { label: "Marketing", value: "marketing" },
  { label: "Healthcare", value: "healthcare" },
  { label: "Consulting", value: "consulting" },
  { label: "Construction", value: "construction" }
]

export default function TemplatesPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedStatus, setSelectedStatus] = useState("all")

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.category.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === "all" || template.category.toLowerCase() === selectedCategory
    const matchesStatus = selectedStatus === "all" || template.status === selectedStatus
    return matchesSearch && matchesCategory && matchesStatus
  })

  const getStatusBadge = (status: string) => {
    const variants = {
      published: { color: "bg-green-100 text-green-800", text: "Published" },
      draft: { color: "bg-yellow-100 text-yellow-800", text: "Draft" },
      archived: { color: "bg-gray-100 text-gray-800", text: "Archived" }
    }
    
    const config = variants[status as keyof typeof variants] || variants.draft
    return <Badge className={config.color}>{config.text}</Badge>
  }

  const getCategoryColor = (category: string) => {
    const colors = {
      technology: "bg-blue-100 text-blue-800",
      marketing: "bg-purple-100 text-purple-800",
      healthcare: "bg-red-100 text-red-800",
      consulting: "bg-green-100 text-green-800",
      construction: "bg-orange-100 text-orange-800"
    }
    return colors[category.toLowerCase() as keyof typeof colors] || "bg-gray-100 text-gray-800"
  }

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-3 h-3 ${i < Math.floor(rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}
      />
    ))
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            RFP Templates
          </h1>
          <p className="text-muted-foreground text-lg">
            Pre-built templates to streamline your RFP creation process
          </p>
        </div>
        <Button 
          size="lg"
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all duration-200"
        >
          <Plus className="mr-2 h-4 w-4" />
          Create Template
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-4">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Templates</CardTitle>
            <div className="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
              <FileText className="h-4 w-4 text-blue-600 dark:text-blue-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">{templates.length}</div>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
              {templates.filter(t => t.status === 'published').length} published
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-green-700 dark:text-green-300">Total Usage</CardTitle>
            <div className="p-2 bg-green-100 dark:bg-green-800 rounded-lg">
              <Eye className="h-4 w-4 text-green-600 dark:text-green-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-900 dark:text-green-100">
              {templates.reduce((sum, t) => sum + t.usageCount, 0)}
            </div>
            <p className="text-xs text-green-600 dark:text-green-400 mt-1">
              Times used this month
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-purple-700 dark:text-purple-300">Avg Rating</CardTitle>
            <div className="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg">
              <Star className="h-4 w-4 text-purple-600 dark:text-purple-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">
              {(templates.reduce((sum, t) => sum + t.rating, 0) / templates.length).toFixed(1)}
            </div>
            <p className="text-xs text-purple-600 dark:text-purple-400 mt-1">
              User satisfaction
            </p>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-orange-700 dark:text-orange-300">Categories</CardTitle>
            <div className="p-2 bg-orange-100 dark:bg-orange-800 rounded-lg">
              <Building2 className="h-4 w-4 text-orange-600 dark:text-orange-300" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">
              {categories.length - 1}
            </div>
            <p className="text-xs text-orange-600 dark:text-orange-400 mt-1">
              Different industries
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Settings className="mr-2 h-4 w-4" />
              Category: {categories.find(c => c.value === selectedCategory)?.label}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {categories.map((category) => (
              <DropdownMenuItem
                key={category.value}
                onClick={() => setSelectedCategory(category.value)}
              >
                {category.label}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <FileText className="mr-2 h-4 w-4" />
              Status: {selectedStatus === 'all' ? 'All' : selectedStatus}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => setSelectedStatus("all")}>
              All Status
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedStatus("published")}>
              Published
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedStatus("draft")}>
              Draft
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSelectedStatus("archived")}>
              Archived
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Templates Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredTemplates.map((template) => (
          <Card key={template.id} className="border-0 shadow-lg hover:shadow-xl transition-all duration-200 group">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <CardTitle className="text-lg">{template.name}</CardTitle>
                  <div className="flex items-center space-x-2">
                    <Badge className={getCategoryColor(template.category)}>
                      {template.category}
                    </Badge>
                    {getStatusBadge(template.status)}
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
                      Preview
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit Template
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Copy className="mr-2 h-4 w-4" />
                      Duplicate
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Download className="mr-2 h-4 w-4" />
                      Export
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-destructive">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              
              <CardDescription className="text-sm">
                {template.description}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Rating and Usage */}
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-1">
                  {renderStars(template.rating)}
                  <span className="text-muted-foreground ml-1">({template.rating})</span>
                </div>
                <div className="text-muted-foreground">
                  {template.usageCount} uses
                </div>
              </div>

              {/* Template Details */}
              <div className="grid grid-cols-2 gap-4 text-sm border-t pt-4">
                <div>
                  <div className="text-muted-foreground">Fields</div>
                  <div className="font-semibold">{template.fields}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Industry</div>
                  <div className="font-semibold">{template.industry}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Author</div>
                  <div className="font-semibold">{template.author}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Modified</div>
                  <div className="font-semibold">{template.lastModified}</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex space-x-2 pt-2">
                <Button size="sm" className="flex-1">
                  <Eye className="mr-2 h-3 w-3" />
                  Use Template
                </Button>
                <Button size="sm" variant="outline">
                  <Download className="mr-2 h-3 w-3" />
                  Export
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Create Template CTA */}
      <Card className="border-dashed border-2">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <FileText className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Create Your First Custom Template</h3>
          <p className="text-muted-foreground text-center mb-4 max-w-md">
            Build reusable RFP templates tailored to your industry and requirements. 
            Save time and ensure consistency across all your proposals.
          </p>
          <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            <Plus className="mr-2 h-4 w-4" />
            Create New Template
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}