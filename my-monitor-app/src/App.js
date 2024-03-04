import React, { useState, useEffect } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import CircularProgress from '@mui/material/CircularProgress'; // Import CircularProgress
import { Typography, Box } from '@mui/material'; // Import Typography for text and Box for layout

const PullRequestList = () => {
  const [pullRequests, setPullRequests] = useState([]);
  const [loading, setLoading] = useState(false); // State to track loading

  useEffect(() => {
    const fetchPullRequests = async () => {
      setLoading(true); // Start loading
      try {
        const response = await fetch('http://ec2-13-60-5-251.eu-north-1.compute.amazonaws.com:8000/api/v1/monitor_router/pull-requests');
        if (!response.ok) {
          throw new Error('Failed to fetch pull requests');
        }
        const data = await response.json();
        setPullRequests(data);
      } catch (error) {
        console.error('Error fetching pull requests:', error);
      } finally {
        setLoading(false); // End loading
      }
    };

    fetchPullRequests();
  }, []);

  // Function to handle image download
  const handleImageDownload = async (screenshotPath) => {
    // Adjusted Base URL to include the complete path to the FastAPI endpoint serving screenshots
    const baseUrl = 'http://ec2-13-60-5-251.eu-north-1.compute.amazonaws.com:8000/api/v1/monitor_router/'; 
    const imageUrl = `${baseUrl}${screenshotPath}`; // Construct the full URL

    try {
      const response = await fetch(imageUrl);
      console.log('Attempting to download image from:', imageUrl);
      console.log('Response:', screenshotPath);
      if (!response.ok) {
        throw new Error('Failed to download image');
      }

      const arrayBuffer = await response.arrayBuffer();
      const blob = new Blob([arrayBuffer], { type: response.headers.get('Content-Type') });

      const blobUrl = URL.createObjectURL(blob);

      // Creating a temporary anchor element for downloading the file
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = screenshotPath.split('/').pop(); // Extract the filename from the path for the download attribute

      // Simulating a click event to trigger the download
      document.body.appendChild(link); // Append to body to ensure it's in the document
      link.click();
      document.body.removeChild(link); // Clean up by removing the link after triggering the download

      // Clean up by revoking the blob URL after a short delay to ensure the download has initiated
      setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
};


return (
  <div>
    <Typography variant="h4" gutterBottom>
      GitHub Pull Requests Monitoring
    </Typography>
    {loading ? (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="300px">
        <CircularProgress />
      </Box>
    ) : (
      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>User</TableCell>
              <TableCell>Download Image</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {pullRequests.map((pr) => (
              <TableRow key={pr.id} hover>
                <TableCell>{pr.id}</TableCell>
                <TableCell>{pr.title}</TableCell>
                <TableCell>{pr.user ? pr.user.login : 'No user information'}</TableCell>
                <TableCell>
                  {pr.screenshot_path && (
                    <button
                      style={{ textDecoration: 'underline', cursor: 'pointer', background: 'none', border: 'none', color: 'blue' }}
                      onClick={() => handleImageDownload(pr.screenshot_path)}
                    >
                      Download
                    </button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )}
  </div>
);
};

export default PullRequestList;