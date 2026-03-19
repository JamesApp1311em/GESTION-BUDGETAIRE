import React, { useState } from "react";
import { 
  Check, 
  Home, 
  GraduationCap, 
  Utensils, 
  CreditCard,
  ChevronLeft,
  ChevronRight,
  Wallet
} from "lucide-react";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";

const mockData = {
  user: "Jean Martin",
  month: "Mars",
  year: "2026",
  income: 2500,
  expenses: {
    loyer: 650,
    scolarite: 180,
    ration: 320,
    dettes: 200,
    poche: 100,
    assistance: 150,
    autres: 80,
  }
};

const steps = [
  { id: 1, name: "Période", status: "complete" },
  { id: 2, name: "Revenu", status: "complete" },
  { id: 3, name: "Dépenses", status: "current" },
  { id: 4, name: "Résultats", status: "upcoming" },
];

export default function WizardVariant() {
  const [expenses, setExpenses] = useState({
    loyer: mockData.expenses.loyer.toString(),
    scolarite: mockData.expenses.scolarite.toString(),
    ration: mockData.expenses.ration.toString(),
    dettes: mockData.expenses.dettes.toString(),
  });

  const totalExpenses = Object.values(expenses).reduce((acc, val) => acc + (parseFloat(val) || 0), 0);
  const remaining = mockData.income - totalExpenses;

  const handleExpenseChange = (field: keyof typeof expenses, value: string) => {
    setExpenses(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-slate-50 p-4 md:p-8 font-sans flex justify-center">
      <div className="max-w-4xl w-full space-y-8">
        
        {/* Header / Stepper */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-slate-900 mb-1">Bienvenue, {mockData.user}</h1>
            <p className="text-slate-500">Commençons votre budget de {mockData.month} {mockData.year}.</p>
          </div>

          <div className="relative">
            <div className="absolute top-4 left-0 w-full h-0.5 bg-slate-100 -z-10" />
            <div className="absolute top-4 left-0 w-[60%] h-0.5 bg-blue-600 -z-10 transition-all duration-500" />
            
            <div className="flex justify-between">
              {steps.map((step) => (
                <div key={step.id} className="flex flex-col items-center gap-2">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium border-2
                    ${step.status === 'complete' ? 'bg-blue-600 border-blue-600 text-white' : ''}
                    ${step.status === 'current' ? 'bg-white border-blue-600 text-blue-600' : ''}
                    ${step.status === 'upcoming' ? 'bg-white border-slate-200 text-slate-400' : ''}
                  `}>
                    {step.status === 'complete' ? <Check className="w-4 h-4" /> : step.id}
                  </div>
                  <span className={`text-sm font-medium ${step.status === 'upcoming' ? 'text-slate-400' : 'text-slate-700'}`}>
                    {step.name}
                  </span>
                </div>
              ))}
            </div>
          </div>
          
          <div className="mt-8">
            <div className="flex justify-between text-sm text-slate-500 mb-2">
              <span>Progression</span>
              <span>75%</span>
            </div>
            <Progress value={75} className="h-2" />
          </div>
        </div>

        {/* Main Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Wizard Form */}
          <Card className="lg:col-span-2 border-slate-200 shadow-sm">
            <CardHeader className="pb-4">
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-xl text-slate-800">3. Ventilation des Dépenses</CardTitle>
                  <CardDescription className="text-base mt-1">Entrez chaque catégorie de dépense pour ce mois.</CardDescription>
                </div>
                <div className="text-right bg-blue-50 px-4 py-2 rounded-lg border border-blue-100">
                  <p className="text-xs font-medium text-blue-600 uppercase tracking-wider mb-1">Reste à allouer</p>
                  <p className={`text-2xl font-bold ${remaining < 0 ? 'text-red-600' : 'text-blue-700'}`}>
                    ${remaining.toLocaleString()}
                  </p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              
              <div className="space-y-4">
                {/* Loyer */}
                <div className="flex items-center gap-4 group">
                  <div className="w-12 h-12 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-500 group-hover:bg-indigo-100 transition-colors">
                    <Home className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <Label htmlFor="loyer" className="text-base font-medium text-slate-700">Loyer</Label>
                    <p className="text-sm text-slate-500">Logement et charges</p>
                  </div>
                  <div className="relative w-40">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
                    <Input 
                      id="loyer" 
                      type="number" 
                      className="pl-7 text-lg font-medium" 
                      value={expenses.loyer}
                      onChange={(e) => handleExpenseChange('loyer', e.target.value)}
                    />
                  </div>
                </div>

                <Separator />

                {/* Scolarité */}
                <div className="flex items-center gap-4 group">
                  <div className="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-500 group-hover:bg-amber-100 transition-colors">
                    <GraduationCap className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <Label htmlFor="scolarite" className="text-base font-medium text-slate-700">Scolarité</Label>
                    <p className="text-sm text-slate-500">Frais d'études et matériel</p>
                  </div>
                  <div className="relative w-40">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
                    <Input 
                      id="scolarite" 
                      type="number" 
                      className="pl-7 text-lg font-medium" 
                      value={expenses.scolarite}
                      onChange={(e) => handleExpenseChange('scolarite', e.target.value)}
                    />
                  </div>
                </div>

                <Separator />

                {/* Ration */}
                <div className="flex items-center gap-4 group">
                  <div className="w-12 h-12 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-500 group-hover:bg-emerald-100 transition-colors">
                    <Utensils className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <Label htmlFor="ration" className="text-base font-medium text-slate-700">Ration</Label>
                    <p className="text-sm text-slate-500">Alimentation et courses</p>
                  </div>
                  <div className="relative w-40">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
                    <Input 
                      id="ration" 
                      type="number" 
                      className="pl-7 text-lg font-medium" 
                      value={expenses.ration}
                      onChange={(e) => handleExpenseChange('ration', e.target.value)}
                    />
                  </div>
                </div>

                <Separator />

                {/* Dettes */}
                <div className="flex items-center gap-4 group">
                  <div className="w-12 h-12 rounded-xl bg-rose-50 flex items-center justify-center text-rose-500 group-hover:bg-rose-100 transition-colors">
                    <CreditCard className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <Label htmlFor="dettes" className="text-base font-medium text-slate-700">Dettes</Label>
                    <p className="text-sm text-slate-500">Remboursements</p>
                  </div>
                  <div className="relative w-40">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">$</span>
                    <Input 
                      id="dettes" 
                      type="number" 
                      className="pl-7 text-lg font-medium" 
                      value={expenses.dettes}
                      onChange={(e) => handleExpenseChange('dettes', e.target.value)}
                    />
                  </div>
                </div>

              </div>

            </CardContent>
            <CardFooter className="bg-slate-50/50 flex justify-between py-6 border-t border-slate-100">
              <Button variant="ghost" className="text-slate-500 hover:text-slate-800">
                <ChevronLeft className="w-4 h-4 mr-2" /> Retour
              </Button>
              <Button className="bg-blue-600 hover:bg-blue-700 text-white px-8">
                Continuer <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            </CardFooter>
          </Card>

          {/* Sidebar Summary */}
          <div className="space-y-6">
            <Card className="border-slate-200 shadow-sm bg-white">
              <CardHeader className="pb-3 border-b border-slate-100">
                <CardTitle className="text-lg text-slate-800 flex items-center gap-2">
                  <Wallet className="w-5 h-5 text-blue-600" /> Résumé
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4 space-y-4">
                
                <div>
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Étape 1 : Période</p>
                  <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="font-medium text-slate-700">Mois</span>
                    <span className="text-slate-900 font-semibold">{mockData.month} {mockData.year}</span>
                  </div>
                </div>

                <div>
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Étape 2 : Revenu</p>
                  <div className="flex justify-between items-center bg-slate-50 p-3 rounded-lg border border-slate-100">
                    <span className="font-medium text-slate-700">Revenu Total</span>
                    <span className="text-emerald-600 font-semibold">${mockData.income.toLocaleString()}</span>
                  </div>
                </div>

                <Separator />
                
                <div>
                  <p className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">En cours</p>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-slate-700">Dépenses saisies</span>
                    <span className="text-slate-900 font-semibold">${totalExpenses.toLocaleString()}</span>
                  </div>
                </div>

              </CardContent>
            </Card>
          </div>

        </div>
      </div>
    </div>
  );
}
